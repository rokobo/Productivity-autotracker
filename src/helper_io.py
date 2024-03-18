"""
Collection of helper functions for input and output rountines.
"""
# pylint: disable=broad-exception-caught, possibly-unused-variable
# pylint: disable=unused-argument
import sys
from os.path import dirname, exists, join, abspath
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import Callable, TypeVar, Any, Optional
import sqlite3 as sql
import yaml
from notifypy import Notify
import pandas as pd

log_path = join(dirname(dirname(abspath(__file__))), "logs")
logger1 = logging.getLogger('retry')
logger1.setLevel(logging.DEBUG)
file_handler1 = RotatingFileHandler(
    join(log_path, 'retry.log'), maxBytes=1024*256, backupCount=3)
file_handler1.setLevel(logging.DEBUG)
file_handler1.setFormatter(
    logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
logger1.addHandler(file_handler1)

logger2 = logging.getLogger('activity')
logger2.setLevel(logging.DEBUG)
file_handler2 = RotatingFileHandler(
    join(log_path, 'activity.log'), maxBytes=1024*160, backupCount=3)
file_handler2.setLevel(logging.DEBUG)
file_handler2.setFormatter(
    logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
logger2.addHandler(file_handler2)

T = TypeVar('T')


def retry(
    attempts: int = 0, wait: float = 0.5, print_fail: bool = False,
    log_args: bool = False, log_result: bool = False
) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """
    Retry decorator for any function.

    Args:
        attempts (int, optional): Attempts to execute function.
            Defaults to retry attemps defined in configuration file.
        wait (float, optional): Wait time in between attempts. Defaults to 0.5.

    Returns:
        Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
            Returns decorator that wraps the function with the retry mechanism.
    """
    attempts = load_config()["RETRY_ATTEMPS"] if attempts == 0 else attempts

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        """
        Decorator function that applies the retry mechanism.

        Args:
            func (Callable[..., T]): Function to be wrapped.

        Returns:
            Callable[..., Optional[T]]: Wrapped function with retry logic.
        """
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            """
            Wrapper function that executes the retries.

            Args:
                *args (Any): Variable length arg list for wrapped function.
                **kwargs (Any): Arbitrary keyword args for wrapped function.

            Returns:
                Optional[T]: Wrapped function return or None if all tries fail.
            """
            for attempt in range(attempts):
                try:
                    t1 = time.time()
                    result = func(*args, **kwargs)
                    t2 = time.time()
                except Exception as e:
                    logger1.error(
                        "Error at function %s(%s) on attempt %i: %s(\"%s\")",
                        func.__name__,
                        ', '.join(map(str, args)) if log_args else "",
                        attempt + 1,
                        type(e).__name__,
                        e
                    )
                    if print_fail:
                        print(
                            f"\033[93m{time.strftime('%X')}",
                            f"Error at {func.__name__}(),",
                            "seek app logs \033[00m"
                        )
                    time.sleep(wait)
                    continue
                else:
                    if log_result:
                        logger2.info(
                            "%s(), %.3f seconds, result: %s",
                            func.__name__, t2-t1, result
                        )
                return result
            return None
        return wrapper
    return decorator


def load_yaml(name: str) -> dict:
    """
    Loads yaml file with the provided name using workspace as base dir.

    Args:
        name (str): Partial path string.

    Returns:
        dict: Configuration file.
    """
    workspace = dirname(dirname(abspath(__file__)))
    path = join(workspace, name)
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    for _ in range(5):
        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        if isinstance(config, dict):
            break
        time.sleep(0.1)
    else:
        print(f"{name} file failed to load\033[00m")
        sys.exit()
    return config


def load_config() -> dict[str, Any]:
    """
    Loads the configuration file.

    Returns:
        dict[str, Any]: Dictionary config file.
    """
    workspace = dirname(dirname(abspath(__file__)))
    config = load_yaml("config/config.yml")

    config["WORKSPACE"] = workspace
    config["ASSETS"] = join(workspace, "assets/")
    config["BACKUP"] = join(workspace, "backup/")
    app_name = "Productivity Dashboard - Study Advisor"
    config["NOTIFICATION"] = Notify(
        default_notification_application_name=app_name,
        default_notification_icon=join(
            workspace, join(workspace, "assets/sprout.gif")
        ),
    )
    return config


def load_categories() -> dict[str, Any]:
    """
    Loads the categories configuration file.

    Returns:
        dict[str, Any]: Dictionary config file.
    """
    return load_yaml("config/categories.yml")


@retry(wait=0.1)
def start_databases() -> None:
    """Initializes databases with proper schema."""
    cfg = load_config()
    path = join(cfg["WORKSPACE"], "data/activity.db")
    tables = [
        "activity", "categories", "totals", "settings", "activity_view"
    ]
    if not exists(path):
        conn = sql.connect(path)
        assert conn is not None, "conn is None"
        cursor = conn.cursor()
        for table in tables:
            schema_path = join(
                cfg["WORKSPACE"], f'schema/{table}_schema.sql'
            )
            with open(schema_path, 'r', encoding='utf-8') as file:
                schema = file.read()
            cursor.executescript(schema)
        conn.commit()
        conn.close()

    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    cursor = conn.cursor()
    q = "INSERT OR REPLACE INTO settings (label, value) VALUES (?, ?)"
    cursor.execute(
        q, ("total_offset", f"{cfg['GMT_OFFSET']} hours"))
    cursor.execute(
        q, ("gmt_offset", str(cfg['GMT_OFFSET'])))
    conn.commit()
    conn.close()

    # Start these to prevent errors from last interruption
    save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'mouse')
    save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'keyboard')
    save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'frontend')
    save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'backend')
    save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'audio')


@retry(wait=0.3, log_args=True)
def load_latest_row(name: str) -> pd.DataFrame:
    """
    Loads latest row of a given dataframe.

    Returns:
        pd.DataFrame: Accessed dataframe.
    """
    # Check if file does not exists
    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    # Access database
    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    dataframe = pd.read_sql(
        f"SELECT *, rowid FROM {name} ORDER BY rowid DESC LIMIT 1", conn
    )
    assert isinstance(dataframe, pd.DataFrame), "Not a dataframe"
    assert not dataframe.empty, "Empty dataframe"
    conn.close()
    return dataframe


@retry(wait=0.1)
def load_day_total(day: int) -> pd.DataFrame:
    """
    Loads the total times from the given day.
    Today is 0, yesterday is 1.

    Returns:
        pd.DataFrame: Accessed dataframe.
    """
    # Check if file does not exists
    cfg = load_config()
    path = join(cfg["WORKSPACE"], "data/activity.db")
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()
    if (day > 363) or not isinstance(day, int):
        print("\033[93mInvalid argument error\033[00m")
        sys.exit()

    # Access database
    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    dataframe = pd.read_sql(
        f"SELECT Neutral, Personal, Work \
            FROM totals WHERE days_since = '{day}'", conn
    )
    assert isinstance(dataframe, pd.DataFrame), "Not a dataframe"
    assert not dataframe.empty, "Empty dataframe"
    conn.close()
    return dataframe


@retry(wait=0.1)
def modify_latest_row(
    name: str, new_row: pd.DataFrame, columns_to_update: list[str]
) -> None:
    """
    Modifies the latest row of a dataframe with the provided new_row.

    Args:
        name (str): Name of database.
        new_row (pd.DataFrame): New row of database.
        columns_to_update (list[str]): List of columns to update.
    """
    # Check if file does not exists
    if not isinstance(new_row, pd.DataFrame):
        print("\033[93mWrong argument passed\033[00m")
        sys.exit()
    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    # Access database
    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    cursor = conn.cursor()
    for col in columns_to_update:
        rowid = new_row.loc[0, "rowid"]
        val = new_row.loc[0, col]
        if isinstance(val, str):
            val = f'"{val}"'
        cursor.execute(
            f"UPDATE {name} SET {col} = {val} WHERE rowid = {rowid}"
        )
    conn.commit()
    conn.close()


@retry(wait=0.1)
def append_to_database(name: str, new_row: pd.DataFrame) -> None:
    """
    Appends row to dataframe with the provided new_row.

    Args:
        name (str): Name of database.
        new_row (pd.DataFrame): New row of database.
    """
    if not isinstance(new_row, pd.DataFrame):
        print("\033[93mWrong argument passed\033[00m")
        sys.exit()

    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    new_row.to_sql(name, conn, if_exists="append", index=False)
    conn.close()


@retry(wait=0.1)
def load_activity_between(
    start: int, end: int, name: str = "activity"
) -> pd.DataFrame:
    """
    Loads events in activity database between the start and end timestamp.

    Args:
        start (int): start timestamp.
        end (int): end timestamp.

    Returns:
        pd.DataFrame: Accessed dataframe.
        name (str, optional): database name. Defaults to "activity".
    """
    # Check if file does not exists
    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    # Access database
    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    dataframe = pd.read_sql(
        f"SELECT *, rowid FROM {name}\
            WHERE start_time >= {start} AND end_time <= {end}",
        conn,
    )
    assert isinstance(dataframe, pd.DataFrame), "Not a dataframe"
    assert not dataframe.empty, "Empty dataframe"
    conn.close()
    return dataframe


@retry(wait=0.1)
def load_dataframe(
    name: str, can_be_empty=False, table: Optional[str] = None,
    load_rowid=True, where_cond: Optional[tuple] = None
) -> pd.DataFrame:
    """
    Loads entire database with the provided name.

    Args:
        name (str): Database name.
        can_be_empty (bool, optional): If df can be empty. Defaults to False.
        table (str, optional): Table name, otherwise use database name to
            access it. Defaults to None.
        load_rowid (bool, optional): Select rowid. Defaults to True.
        where_cond (tuple, optional): Used for WHERE clause. Defaults to True.
            "count > 3" should be passed as ("count", ">", 3)

    Returns:
        pd.DataFrame: Accessed dataframe.
    """
    # Check if file does not exists
    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    # Access database
    table = name if table is None else table

    query = f"SELECT *{', rowid' if load_rowid else ''} "
    query += f"FROM {table} "
    if isinstance(where_cond, tuple) and len(where_cond) == 3:
        query += f"WHERE {where_cond[0]} {where_cond[1]} '{where_cond[2]}'"

    conn = sql.connect(path)
    dataframe = pd.read_sql(query, conn)
    assert isinstance(dataframe, pd.DataFrame), "Not a dataframe"
    if not can_be_empty:
        assert not dataframe.empty, "Empty dataframe"
    conn.close()
    return dataframe


@retry(wait=0.1)
def save_dataframe(df: pd.DataFrame, name: str, table: Optional[str] = None):
    """
    Saves dataframe to .db file.

    Args:
        dataframe (pd.DataFrame): Dataframe to be saved.
        path (str): Location the dataframe will be saved.
    """
    if not isinstance(df, pd.DataFrame):
        print("\033[93mWrong argument passed\033[00m")
        sys.exit()
    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    table = name if table is None else table

    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    conn.execute("BEGIN EXCLUSIVE")
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()


def load_input_time(name: str) -> int:
    """
    Will return the time of last input from path.

    Args:
        path (str): Path of last input dataframe.

    Returns:
        int: Time of latest input from path.
    """
    device = load_latest_row(name)
    if device is None:
        return -1
    recorded_time = device.iloc[0, 0]
    return recorded_time


@retry(wait=0.1)
def load_url(page_title: str) -> pd.DataFrame:
    """
    Access the URL by title that was provided by the browser extension.

    Args:
        page_title (str): Title of the page.

    Returns:
        str: URL of the page.
    """
    cfg = load_config()
    path = join(cfg["WORKSPACE"], "data/urls.db")
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    # Load the file and output list of URLs
    query = """
        SELECT *, rowid FROM urls
        WHERE title = ?
    """
    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    url = pd.read_sql(query, conn, params=[page_title])
    assert isinstance(url, pd.DataFrame), "Not a URL dataframe"
    conn.close()
    return url


@retry(wait=0.1)
def set_idle():
    """Function that sets all input databases to idle state."""
    time.sleep(1)
    cfg = load_config()
    now = int(time.time())
    idle_time = cfg["IDLE_TIME"]
    inputs = ["mouse", "keyboard", "audio"]

    for input_name in inputs:
        input_dataframe = load_latest_row(input_name)
        assert input_dataframe is not None, "Failed to get latest row"
        if now - input_dataframe.loc[0, "time"] < idle_time:
            input_dataframe.loc[0, "time"] = now - idle_time
            modify_latest_row(input_name, input_dataframe, ["time"])


def timestamp_to_day(values: pd.Series) -> pd.Series:
    """
    Converts timestamps from a pd.Series into dates yyyy-mm-dd.

    Args:
        values (pd.Series): Timestamp series.

    Returns:
        pd.Series: Dates series.
    """
    cfg = load_config()
    dates = (
        pd.to_datetime(values, unit="s")
        + pd.Timedelta(cfg["GMT_OFFSET"], unit="h")
    ).dt.date
    return dates


def send_notification(
    title: str, message: str, audio: str = "notification"
) -> None:
    """
    Sends a desktop notification with the title and message.
    Waits 12 seconds for message to go away and a little more.

    Args:
        title (str): Title of the notification.
        message (str): Message of the notification.
        audio (str): Desired audio to play.
    """
    cfg = load_config()
    notification = cfg["NOTIFICATION"]
    notification.title = title
    notification.message = message
    notification.audio = join(cfg["WORKSPACE"], "assets", audio + ".wav")
    notification.send(block=False)
    time.sleep(12)


def check_dataframe(name: str) -> bool:
    """
    Checks if database with the provided name exists.

    Returns:
        bool: If the dataframe exists.
    """
    # Check if file does not exists
    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    return exists(path)


@retry(wait=0.1)
def delete_from_dataframe(name: str, column: str, values: list) -> None:
    """
    Deletes values from database by checking matches in the provided column.

    Args:
        name (str): Name of database.
        column (str): Column of database.
        values (list): List of values to delete.
    """
    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    query = f"DELETE FROM {name} \
        WHERE {column} \
            IN ({', '.join('?' for _ in values)})"

    conn = sql.connect(path)
    assert conn is not None, "conn is None"
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()
