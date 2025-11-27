import os
import logging
import json
import tempfile
import datetime
import time
from dateutil import tz
import pyodbc
from azure.storage.blob import BlobServiceClient, ContentSettings
import azure.functions as func

# Config from environment
STORAGE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "archive")
SQL_CONN = os.getenv("SQL_ODBC_CONNECTION")
ARCHIVE_BATCH_SIZE = int(os.getenv("ARCHIVE_BATCH_SIZE", "1000"))
DELETE_BATCH_SIZE = int(os.getenv("DELETE_BATCH_SIZE", "1000"))
TIME_WINDOW_DAYS = int(os.getenv("TIME_WINDOW_DAYS", "30"))

# Column names - change if your schema differs
PK_COL = "Id"
DATE_COL = "OrderDate"
TABLE_NAME = "Orders"

if not STORAGE_CONN_STR:
    raise Exception("AZURE_STORAGE_CONNECTION_STRING is required")
if not SQL_CONN:
    raise Exception("SQL_ODBC_CONNECTION is required")

logger = logging.getLogger("TimerArchiveFunction")
logger.setLevel(logging.INFO)


def get_cutoff_datetime_utc(days):
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(days=days)
    return cutoff


def rows_generator_and_write_ids(temp_id_file_path, cutoff_dt, batch_size=1000):
    """
    Generator that yields NDJSON bytes for upload_blob.
    It pulls rows from SQL in batches and writes their IDs to a temp file.
    """
    conn = pyodbc.connect(SQL_CONN, autocommit=False)
    cursor = conn.cursor()

    # We'll page using PK order. This requires PK is sortable.
    last_id = None
    more = True
    try:
        while more:
            # Build query to fetch a batch; adjust WHERE to use DATE_COL and PK ordering
            # Use parameterized query
            if last_id is None:
                sql = f"""
                SELECT TOP (?) {PK_COL}, * 
                FROM {TABLE_NAME}
                WHERE {DATE_COL} < ?
                ORDER BY {PK_COL} ASC
                """
                params = (batch_size, cutoff_dt)
            else:
                sql = f"""
                SELECT TOP (?) {PK_COL}, *
                FROM {TABLE_NAME}
                WHERE {DATE_COL} < ?
                  AND {PK_COL} > ?
                ORDER BY {PK_COL} ASC
                """
                params = (batch_size, cutoff_dt, last_id)

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            if not rows:
                more = False
                break

            # For each row, convert to JSON line and yield
            for row in rows:
                # pyodbc.Row behaves like tuple with .cursor_description for columns
                # Build dict dynamically
                row_dict = {}
                desc = [d[0] for d in cursor.description]
                for idx, col in enumerate(desc):
                    val = row[idx]
                    # convert datetimes to ISO strings
                    if isinstance(val, datetime.datetime):
                        val = val.isoformat()
                    row_dict[col] = val

                # Write id to temp file for later deletion
                with open(temp_id_file_path, "a", encoding="utf-8") as fids:
                    fids.write(str(row_dict[PK_COL]) + "\n")

                # yield bytes line
                ndjson_line = json.dumps(row_dict, default=str) + "\n"
                yield ndjson_line.encode("utf-8")

            # set last_id for next page
            last_id = getattr(rows[-1], 0)  # first column is PK_COL
            # If returned rows < batch_size then done next iteration will stop
            if len(rows) < batch_size:
                more = False

    finally:
        cursor.close()
        conn.close()


def count_to_archive(cutoff_dt):
    conn = pyodbc.connect(SQL_CONN, autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(1) FROM {TABLE_NAME} WHERE {DATE_COL} < ?", (cutoff_dt,))
        cnt = cur.fetchone()[0]
        return cnt
    finally:
        cur.close()
        conn.close()


def delete_ids_from_file_in_batches(temp_id_file_path, delete_batch_size=1000):
    """
    Read IDs from file and delete them from SQL in batches inside transactions.
    Returns total deleted count.
    """
    conn = pyodbc.connect(SQL_CONN, autocommit=False)
    cur = conn.cursor()
    total_deleted = 0
    try:
        # Read IDs in streaming fashion
        def id_stream():
            with open(temp_id_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    l = line.strip()
                    if l:
                        yield l

        batch = []
        for idstr in id_stream():
            batch.append(idstr)
            if len(batch) >= delete_batch_size:
                # delete these in a transaction
                placeholders = ",".join("?" for _ in batch)
                delete_sql = f"DELETE FROM {TABLE_NAME} WHERE {PK_COL} IN ({placeholders})"
                try:
                    cur.execute("BEGIN TRAN")
                    cur.execute(delete_sql, batch)
                    deleted = cur.rowcount
                    cur.execute("COMMIT")
                    total_deleted += deleted
                except Exception as e:
                    cur.execute("ROLLBACK")
                    logger.exception("Error deleting batch - rolled back")
                    raise
                batch = []

        # delete remainder
        if batch:
            placeholders = ",".join("?" for _ in batch)
            delete_sql = f"DELETE FROM {TABLE_NAME} WHERE {PK_COL} IN ({placeholders})"
            try:
                cur.execute("BEGIN TRAN")
                cur.execute(delete_sql, batch)
                deleted = cur.rowcount
                cur.execute("COMMIT")
                total_deleted += deleted
            except Exception as e:
                cur.execute("ROLLBACK")
                logger.exception("Error deleting final batch - rolled back")
                raise

        return total_deleted

    finally:
        cur.close()
        conn.close()


def build_blob_path(now_utc):
    y = now_utc.strftime("%Y")
    m = now_utc.strftime("%m")
    d = now_utc.strftime("%d")
    ts = now_utc.strftime("%Y%m%dT%H%M%SZ")
    blob_name = f"archive/orders/{y}/{m}/{d}/orders{ts}.ndjson"
    return blob_name


def main(mytimer: func.TimerRequest) -> None:
    start_time = time.time()
    logger.info("TimerArchiveFunction started")
    cutoff_dt = get_cutoff_datetime_utc(TIME_WINDOW_DAYS)
    logger.info(f"Cutoff datetime (UTC) for archiving rows older than {TIME_WINDOW_DAYS} days: {cutoff_dt.isoformat()}")

    # Count how many rows to archive
    try:
        total_to_archive = count_to_archive(cutoff_dt)
        if total_to_archive == 0:
            logger.info("No rows to archive. Exiting.")
            return
        logger.info(f"Rows to archive: {total_to_archive}")
    except Exception:
        logger.exception("Failed to count rows to archive")
        raise

    # Create temp file to collect IDs
    temp_ids_fd, temp_ids_path = tempfile.mkstemp(prefix="archived_ids_", text=True)
    os.close(temp_ids_fd)  # we'll open normally by name

    # Build blob name
    now_utc = datetime.datetime.utcnow()
    blob_name = build_blob_path(now_utc)

    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONN_STR)
    container_client = blob_service.get_container_client(BLOB_CONTAINER)
    try:
        container_client.create_container()
    except Exception:
        # ignore if exists or not allowed
        pass

    blob_client = container_client.get_blob_client(blob_name)

    # Upload NDJSON by streaming generator
    try:
        gen = rows_generator_and_write_ids(temp_ids_path, cutoff_dt, batch_size=ARCHIVE_BATCH_SIZE)
        logger.info(f"Starting upload to blob: {blob_name}")
        # Stream upload - upload_blob accepts generator of bytes
        blob_client.upload_blob(gen, overwrite=True, content_settings=ContentSettings(content_type="application/x-ndjson"))
        logger.info("Upload complete")
    except Exception:
        logger.exception("Failed to upload archive blob. Will cleanup temp file and exit without deleting SQL rows.")
        try:
            os.remove(temp_ids_path)
        except Exception:
            pass
        raise

    # After successful upload, delete rows by ids recorded in temp file
    try:
        deleted = delete_ids_from_file_in_batches(temp_ids_path, delete_batch_size=DELETE_BATCH_SIZE)
        # Log success: number of archived rows and blob URL
        blob_url = blob_client.url
        logger.info(f"Archived rows: {deleted}; Archive blob: {blob_url}")
    except Exception:
        logger.exception("Failed to delete archived rows after upload. Manual intervention may be required.")
        raise
    finally:
        try:
            os.remove(temp_ids_path)
        except Exception:
            pass

    elapsed = time.time() - start_time
    logger.info(f"TimerArchiveFunction finished in {elapsed:.2f}s")
