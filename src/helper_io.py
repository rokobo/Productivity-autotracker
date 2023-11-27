"""
Collection of helper functions for input and output rountines.
"""
# pylint: disable=broad-exception-caught, possibly-unused-variable
# pylint: disable=unused-argument
import sys
from os.path import dirname, exists, join, abspath
import time
from datetime import datetime, timedelta
import sqlite3 as sql
import yaml
from notifypy import Notify
import pandas as pd


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


def load_config() -> dict[str, any]:
    """
    Loads the configuration file.

    Returns:
        dict[str, any]: Dictionary config file.
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


def load_categories() -> dict[str, any]:
    """
    Loads the categories configuration file.

    Returns:
        dict[str, any]: Dictionary config file.
    """
    return load_yaml("config/categories.yml")


def start_databases() -> None:
    """Initializes databases with proper schema."""
    cfg = load_config()
    path = join(cfg["WORKSPACE"], "data/activity.db")
    tables = ["activity", "categories", "totals", "settings", "activity_view"]
    if not exists(path):
        for _ in range(cfg["RETRY_ATTEMPS"]):
            try:
                conn = sql.connect(path)
                cursor = conn.cursor()
                for table in tables:
                    schema_path = join(
                        cfg["WORKSPACE"], f'schema/{table}_schema.sql'
                    )
                    with open(schema_path, 'r', encoding='utf-8') as file:
                        schema = file.read()
                    cursor.executescript(schema)
                conn.commit()
            except Exception:
                time.sleep(0.1)
            else:
                conn.close()
                break
        else:
            conn.close()
            print("\033[93mFailed to create database\033[00m")
            sys.exit()
        conn.close()

    for _ in range(cfg["RETRY_ATTEMPS"]):
        try:
            conn = sql.connect(path)
            cursor = conn.cursor()
            q = "INSERT OR REPLACE INTO settings (label, value) VALUES (?, ?)"
            cursor.execute(
                q, ("total_offset", f"{cfg['GMT_OFFSET']} hours"))
            cursor.execute(
                q, ("gmt_offset", str(cfg['GMT_OFFSET'])))
            conn.commit()
        except Exception:
            time.sleep(0.1)
        else:
            conn.close()
            break
    else:
        conn.close()
        print("\033[93mFailed to configure database\033[00m")
        sys.exit()
    conn.close()


def load_lastest_row(name: str) -> pd.DataFrame:
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
    retries = cfg["RETRY_ATTEMPS"]
    for _ in range(retries):
        conn = sql.connect(path)
        dataframe = pd.read_sql(
            f"SELECT *, rowid FROM {name} ORDER BY rowid DESC LIMIT 1", conn
        )
        if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
            break
        time.sleep(0.1)
    else:
        conn.close()
        print("\033[93mFailed to load latest row\033[00m")
        sys.exit()
    conn.close()
    return dataframe


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

    # Access database
    day_str = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
    retries = cfg["RETRY_ATTEMPS"]
    for _ in range(retries):
        conn = sql.connect(path)
        dataframe = pd.read_sql(
            f"SELECT Neutral, Personal, Work \
                FROM totals WHERE day = '{day_str}'", conn
        )
        if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
            break
        time.sleep(0.1)
    else:
        conn.close()
        print("\033[93mFailed to load day total\033[00m")
        sys.exit()
    conn.close()
    return dataframe


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
    retries = cfg["RETRY_ATTEMPS"]
    for _ in range(retries):
        try:
            conn = sql.connect(path)
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
        except Exception as e:
            print(e)
            time.sleep(0.1)
        else:
            conn.close()
            break
    else:
        conn.close()
        print("\033[93mFailed to modify latest row\033[00m")
        sys.exit()
    conn.close()


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

    retries = cfg["RETRY_ATTEMPS"]
    for _ in range(retries):
        try:
            conn = sql.connect(path)
            new_row.to_sql(name, conn, if_exists="append", index=False)
        except Exception:
            time.sleep(0.1)
        else:
            conn.close()
            break
    else:
        conn.close()
        print("\033[93mFailed to append to database\033[00m")
        sys.exit()
    conn.close()


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
    retries = cfg["RETRY_ATTEMPS"]
    for _ in range(retries):
        conn = sql.connect(path)
        dataframe = pd.read_sql(
            f"SELECT *, rowid FROM {name}\
                WHERE start_time >= {start} AND end_time <= {end}",
            conn,
        )
        if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
            break
        time.sleep(0.1)
    else:
        conn.close()
        print("\033[93mFailed to load activity between\033[00m")
        sys.exit()
    conn.close()
    return dataframe


def load_dataframe(
    name: str, can_be_empty=False, table: str = None, load_rowid=True
) -> pd.DataFrame:
    """
    Loads entire database with the provided name.

    Args:
        name (str): Database name.
        can_be_empty (bool, optional): If df can be empty. Defaults to False.
        table (str, optional): Table name, otherwise use database name to
            access it. Defaults to None.
        load_rowid (bool, optional): Select rowid. Defaults to True.

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
    retries = cfg["RETRY_ATTEMPS"]
    for _ in range(retries):
        conn = sql.connect(path)
        dataframe = pd.read_sql(f"SELECT *{', rowid' if load_rowid else ''} \
            FROM {table}", conn)
        if isinstance(dataframe, pd.DataFrame):
            break
        if can_be_empty or not dataframe.empty:
            break
        time.sleep(0.1)
    else:
        conn.close()
        print(f"\033[93mFailed to load {name} dataframe\033[00m")
        sys.exit()
    conn.close()
    return dataframe


def save_dataframe(dataframe: pd.DataFrame, name: str, table: str = None):
    """
    Saves dataframe to .db file.

    Args:
        dataframe (pd.DataFrame): Dataframe to be saved.
        path (str): Location the dataframe will be saved.
    """
    if not isinstance(dataframe, pd.DataFrame):
        print("\033[93mWrong argument passed\033[00m")
        sys.exit()
    cfg = load_config()
    path = join(cfg["WORKSPACE"], f"data/{name}.db")
    table = name if table is None else table

    retries = cfg["RETRY_ATTEMPS"]
    for _ in range(retries):
        try:
            conn = sql.connect(path)
            conn.execute("BEGIN EXCLUSIVE")
            dataframe.to_sql(table, conn, if_exists="replace", index=False)
        except Exception:
            time.sleep(0.1)
        else:
            conn.close()
            break
    else:
        conn.close()
        print("\033[93mFailed to save dataframe\033[00m")
        sys.exit()
    conn.close()


def load_input_time(name: str) -> int:
    """
    Will return the time of last input from path.

    Args:
        path (str): Path of last input dataframe.

    Returns:
        int: Time of latest input from path.
    """
    device = load_lastest_row(name)
    recorded_time = device.iloc[0, 0]
    return recorded_time


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
    retries = cfg["RETRY_ATTEMPS"]
    query = """
        SELECT *, rowid FROM urls
        WHERE title = ?
    """
    for _ in range(retries):
        conn = sql.connect(path)
        url = pd.read_sql(query, conn, params=[page_title])
        if isinstance(url, pd.DataFrame):
            break
        time.sleep(0.1)
    else:
        conn.close()
        print("\033[93mFailed to load latest URLs\033[00m")
        sys.exit()
    conn.close()
    return url


def set_idle():
    """Function that sets all input databases to idle state."""
    time.sleep(1)
    cfg = load_config()
    now = int(time.time())
    idle_time = cfg["IDLE_TIME"]
    inputs = ["mouse", "keyboard", "audio"]

    for input_name in inputs:
        input_dataframe = load_lastest_row(input_name)
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
    retries = cfg["RETRY_ATTEMPS"]
    if not exists(path):
        print("\033[93mPath does not exist error\033[00m")
        sys.exit()

    query = f"DELETE FROM {name} \
        WHERE {column} \
            IN ({', '.join('?' for _ in values)})"

    for _ in range(retries):
        try:
            conn = sql.connect(path)
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
        except Exception:
            time.sleep(0.1)
        else:
            conn.close()
            break
    else:
        conn.close()
        print("\033[93mFailed to delete dataframe\033[00m")
        sys.exit()
    conn.close()
