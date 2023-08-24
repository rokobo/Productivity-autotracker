"""
Collection of helper functions for input and output rountines.
"""
# pylint: disable=broad-exception-caught, possibly-unused-variable
# pylint: disable=unused-argument, import-error
import os
import time
from notifypy import Notify
import pandas as pd
from helper_retry import try_to_run


def load_config() -> dict[str, any]:
    """
    Loads the configuration file.

    Returns:
        dict[str, any]: Dictionary config file.
    """
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(workspace, "config/config.yml")

    config = try_to_run(
        var='config',
        code='with open(config_path, "r", encoding="utf-8") as file:\
            \n    config = yaml.safe_load(file)',
        error_check='not isinstance(config, dict)',
        final_code='',
        retries=5,
        environment=locals())

    config["WORKSPACE"] = workspace
    config["ASSETS"] = os.path.join(workspace, "assets/")
    app_name = "Productivity Dashboard - Study Advisor"
    config["NOTIFICATION"] = Notify(
        default_notification_application_name=app_name,
        default_notification_icon=os.path.join(
            workspace, "assets\\sprout.gif"),
    )
    return config


def load_categories() -> dict[str, any]:
    """
    Loads the categories configuration file.

    Returns:
        dict[str, any]: Dictionary config file.
    """
    cfg = load_config()
    config_path = os.path.join(cfg["WORKSPACE"], "config/categories.yml")
    categories = try_to_run(
        var='categories',
        code='with open(config_path, "r", encoding="utf-8") as file:\
            \n    categories = yaml.safe_load(file)',
        error_check='not isinstance(categories, dict)',
        final_code='',
        retries=5,
        environment=locals())
    return categories


def load_lastest_row(name: str) -> pd.DataFrame:
    """
    Loads latest row of a given dataframe.

    Returns:
        pd.DataFrame: Accessed dataframe.
    """
    # Check if file does not exists
    cfg = load_config()
    path = os.path.join(cfg["WORKSPACE"], f'data/{name}.db')
    dataframe = pd.DataFrame({})
    assert os.path.exists(path), "Path does not exist error"

    # Access database
    retries = cfg['RETRY_ATTEMPS']
    dataframe = try_to_run(
        var='data',
        code='conn = sql.connect(path)\
            \ndata = pd.read_sql(\
                f"SELECT *, rowid FROM {name}\
                    ORDER BY rowid DESC LIMIT 1", conn)',
        error_check='data.empty or not isinstance(data, pd.DataFrame)',
        final_code='conn.close()',
        retries=retries,
        environment=locals())
    assert not dataframe.empty, "Loaded dataframe is empty error"
    return dataframe


def load_day_total(day: int) -> pd.DataFrame:
    """
    Loads the total times from the given day.
    Today is 364, yesterday is 363.

    Returns:
        pd.DataFrame: Accessed dataframe.
    """
    # Check if file does not exists
    cfg = load_config()
    path = os.path.join(cfg["WORKSPACE"], 'data/totals.db')
    dataframe = pd.DataFrame({})
    assert os.path.exists(path), "Path does not exist error"

    # Access database
    retries = cfg['RETRY_ATTEMPS']
    dataframe = try_to_run(
        var='data',
        code='conn = sql.connect(path)\
            \ndata = pd.read_sql(\
                f"SELECT * FROM totals\
                    WHERE rowid = {day}", conn)',
        error_check='data.empty or not isinstance(data, pd.DataFrame)',
        final_code='conn.close()',
        retries=retries,
        environment=locals())
    assert not dataframe.empty, "Loaded dataframe is empty error"
    return dataframe


def modify_latest_row(
        name: str, new_row: pd.DataFrame,
        columns_to_update: list[str]) -> None:
    """
    Modifies the latest row of a dataframe with the provided new_row.

    Args:
        name (str): Name of database.
        new_row (pd.DataFrame): New row of database.
        columns_to_update (list[str]): List of columns to update.
    """
    # Check if file does not exists
    cfg = load_config()
    path = os.path.join(cfg["WORKSPACE"], f'data/{name}.db')
    assert os.path.exists(path), "Path does not exist error"

    # Access database
    retries = cfg['RETRY_ATTEMPS']
    for col in columns_to_update:
        rowid = new_row.loc[0, 'rowid']
        val = new_row.loc[0, col]
        if isinstance(val, str):
            val = f'"{val}"'
        query = f'UPDATE {name} SET {col} = {val} WHERE rowid = {rowid}'

        try_to_run(
            var='',
            code='conn = sql.connect(path)\
                \ncursor = conn.cursor()\
                \ncursor.execute(query)\
                \nconn.commit()',
            error_check='',
            final_code='conn.close()',
            retries=retries,
            environment=locals())


def append_to_database(name: str, new_row: pd.DataFrame) -> None:
    """
    Appends row to dataframe with the provided new_row.

    Args:
        name (str): Name of database.
        new_row (pd.DataFrame): New row of database.
    """
    cfg = load_config()
    path = os.path.join(cfg["WORKSPACE"], f'data/{name}.db')
    retries = cfg['RETRY_ATTEMPS']

    try_to_run(
        var='',
        code='conn = sql.connect(path)\
            \nnew_row.to_sql(\
                name, conn, if_exists="append", index=False)',
        error_check='not isinstance(new_row, pd.DataFrame)',
        final_code='conn.close()',
        retries=retries,
        environment=locals())


def load_activity_between(
        start: int, end: int, name: str = "activity") -> pd.DataFrame:
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
    path = os.path.join(cfg["WORKSPACE"], f'data/{name}.db')
    dataframe = pd.DataFrame({})
    assert os.path.exists(path), "Path does not exist error"

    # Access database
    retries = cfg['RETRY_ATTEMPS']
    dataframe = try_to_run(
        var='data',
        code='conn = sql.connect(path)\
            \ndata = pd.read_sql(\
                f"SELECT *, rowid FROM {name}\
                    WHERE start_time >= {start} AND end_time <= {end}", conn)',
        error_check='data.empty or not isinstance(data, pd.DataFrame)',
        final_code='conn.close()',
        retries=retries,
        environment=locals())
    assert not dataframe.empty, "Loaded dataframe is empty error"
    return dataframe


def load_dataframe(name: str) -> pd.DataFrame:
    """
    Loads entire database with the provided name.

    Returns:
        pd.DataFrame: Accessed dataframe.
    """
    # Check if file does not exists
    cfg = load_config()
    path = os.path.join(cfg["WORKSPACE"], f'data/{name}.db')
    dataframe = pd.DataFrame({})
    assert os.path.exists(path), "Path does not exist error"

    # Access database
    retries = cfg['RETRY_ATTEMPS']
    dataframe = try_to_run(
        var='data',
        code='conn = sql.connect(path)\
            \ndata = pd.read_sql(f"SELECT *, rowid FROM {name}", conn)',
        error_check='data.empty or not isinstance(data, pd.DataFrame)',
        final_code='conn.close()',
        retries=retries,
        environment=locals())
    assert not dataframe.empty, "Loaded dataframe is empty error"
    return dataframe


def save_dataframe(dataframe: pd.DataFrame, name: str):
    """
    Saves dataframe to .db file.

    Args:
        dataframe (pd.DataFrame): Dataframe to be saved.
        path (str): Location the dataframe will be saved.
    """
    cfg = load_config()
    path = os.path.join(cfg["WORKSPACE"], f'data/{name}.db')
    retries = cfg['RETRY_ATTEMPS']

    try_to_run(
        var='dataframe',
        code='conn = sql.connect(path)\
            \nconn.execute("BEGIN EXCLUSIVE")\
            \ndataframe.to_sql(\
                name, conn, if_exists="replace", index=False)',
        error_check='not isinstance(dataframe, pd.DataFrame)',
        final_code='conn.close()',
        retries=retries,
        environment=locals())


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
    path = os.path.join(cfg["WORKSPACE"], 'data/urls.db')
    assert os.path.exists(path), "Path does not exist error"

    # Load the file and output list of URLs
    retries = cfg['RETRY_ATTEMPS']
    query = """
        SELECT *, rowid FROM urls
        WHERE title = ?
    """
    url = try_to_run(
        var='url',
        code="conn = sql.connect(path)\
            \nurl = pd.read_sql(query , conn, params=[page_title])",
        error_check='not isinstance(url, pd.DataFrame)',
        final_code='conn.close()',
        retries=retries,
        environment=locals())
    return url


def set_idle():
    """Function that sets all input databases to idle state."""
    time.sleep(1)
    cfg = load_config()
    now = int(time.time())
    idle_time = cfg["IDLE_TIME"]
    inputs = ["mouse", "keyboard", "audio", "fullscreen"]

    for input_name in inputs:
        input_dataframe = load_lastest_row(input_name)
        if now - input_dataframe.loc[0, 'time'] < idle_time:
            input_dataframe.loc[0, 'time'] = now - idle_time
            modify_latest_row(input_name, input_dataframe, ['time'])


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
        pd.to_datetime(values, unit='s') +
        pd.Timedelta(cfg["GMT_OFFSET"], unit='h')
    ).dt.date
    return dates


def send_notification(
        title: str, message: str, audio: str = "notification") -> None:
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
    notification.audio = os.path.join(
        cfg["WORKSPACE"], "assets", audio + ".wav")
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
    path = os.path.join(cfg["WORKSPACE"], f'data/{name}.db')
    return os.path.exists(path)
