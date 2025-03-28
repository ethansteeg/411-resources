from contextlib import contextmanager
import logging
import os
import sqlite3

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


# load the db path from the environment with a default value
DB_PATH = os.getenv("DB_PATH", "/app/sql/boxing.db")


def check_database_connection():
    """
    Checks if a connection to the SQLite database can be established.

    This function attempts to connect to the SQLite database specified by DB_PATH and executes a simple query.
    It raises an exception if the connection fails or if a database error occurs.

    Raises:
        Exception: If a database connection error occurs.
    """
    logger.debug("Checking database connection...")


    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Execute a simple query to verify the connection is active
        cursor.execute("SELECT 1;")
        conn.close()
        logger.debug("Database connection check successful.")

    except sqlite3.Error as e:
        error_message = f"Database connection error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

def check_table_exists(tablename: str):
    """
    Checks if a specified table exists in the SQLite database.

    This function connects to the SQLite database and checks if a table with the given name exists.
    It raises an exception if the table does not exist or if a database error occurs.

    Args:
        tablename (str): The name of the table to check.

    Raises:
        Exception: If the table does not exist or if a database error occurs.
    
    """
    logger.debug(f"Checking if table '{tablename}' exists...")


    try:

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Use parameterized query to avoid SQL injection
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tablename,))
        result = cursor.fetchone()

        conn.close()

        if result is None:
            error_message = f"Table '{tablename}' does not exist."
            logger.error(error_message)
            raise Exception(error_message)
        logger.debug(f"Table '{tablename}' exists")

    except sqlite3.Error as e:
        error_message = f"Table check error for '{tablename}': {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

@contextmanager
def get_db_connection():
    """
    Provides a context manager for obtaining a database connection.

    This function yields a database connection that is automatically closed when the context is exited.
    It handles potential SQLite errors during connection establishment.

    Yields:
        sqlite3.Connection: A database connection object.

    Raises:
        sqlite3.Error: If a database error occurs during connection.
    """
    logger.debug("Getting database connection...")
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        logger.debug("Database connection established.")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise e
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed.")
