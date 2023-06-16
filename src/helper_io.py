"""
Collection of helper functions for input and output rountines.
"""
# pylint: disable=broad-exception-caught, possibly-unused-variable
# pylint: disable=unused-argument, import-error
import os
import time
import glob
from threading import Thread
from notifypy import Notify
import pandas as pd
import yaml
from helper_retry import try_to_run


def load_config() -> dict[str, any]:
    """
    Loads the configuration file.

    Returns:
        dict[str, any]: Dictionary config file.
    """
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(workspace, "config/config.yml")
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
    config["WORKSPACE"] = workspace
    app_name = "Productivity Dashboard - Schedule advisor"
    config["NOTIFICATION"] = Notify(
        default_notification_application_name=app_name,
        default_notification_icon=os.path.join(
            workspace, "assets\\sprout.gif"),
    )
    return config


cfg = load_config()


def load_categories() -> dict[str, any]:
    """
    Loads the categories configuration file.

    Returns:
        dict[str, any]: Dictionary config file.
    """
    config_path = os.path.join(cfg["WORKSPACE"], "config/categories.yml")
    with open(config_path, 'r', encoding='utf-8') as categories_file:
        categories = yaml.safe_load(categories_file)
    return categories


def load_lastest_row(name: str) -> tuple[bool, pd.DataFrame]:
    """
    Check if DataFrame is empty and
    creates DataFrame if file is non-existant.

    Returns:
        bool: True if dataframe is accessible and has data.
        pd.DataFrame: Accessed dataframe.
    """
    # Check if file does not exists
    path = os.path.join(cfg["WORKSPACE"], f'{cfg["DATA_PATH"]}{name}.db')
    dataframe = pd.DataFrame({})
    if not os.path.exists(path):
        return False, dataframe

    # Access database
    retries = cfg['RETRY_ATTEMPS']
    dataframe = try_to_run(
        var='dataframe',
        code='conn = sql.connect(path)\
            \ndataframe = pd.read_sql(\
                f"SELECT *, rowid FROM {name}\
                    ORDER BY rowid DESC LIMIT 1", conn)',
        error_check='',
        final_code='conn.close()',
        retries=retries,
        environment=locals())
    return not dataframe.empty, dataframe


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
    path = os.path.join(cfg["WORKSPACE"], f'{cfg["DATA_PATH"]}{name}.db')
    if not os.path.exists(path):
        return

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
                \nconn.execute("BEGIN EXCLUSIVE")\
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
    path = os.path.join(cfg["WORKSPACE"], f'{cfg["DATA_PATH"]}{name}.db')
    retries = cfg['RETRY_ATTEMPS']

    try_to_run(
        var='',
        code='conn = sql.connect(path)\
            \nconn.execute("BEGIN EXCLUSIVE")\
            \nnew_row.to_sql(\
                name, conn, if_exists="append", index=False)',
        error_check='',
        final_code='conn.close()',
        retries=retries,
        environment=locals())


def load_activity_between(
        start: int, end: int, name: str = "activity"
        ) -> tuple[bool, pd.DataFrame]:
    """
    Loads events in activity database between the start and end timestamp.

    Args:
        start (int): start timestamp.
        end (int): end timestamp.

    Returns:
        bool: True if dataframe is accessible and has data.
        pd.DataFrame: Accessed dataframe.
        name (str, optional): database name. Defaults to "activity".
    """
    # Check if file does not exists
    path = os.path.join(cfg["WORKSPACE"], f'{cfg["DATA_PATH"]}{name}.db')
    dataframe = pd.DataFrame({})
    if not os.path.exists(path):
        return False, dataframe

    # Access database
    retries = cfg['RETRY_ATTEMPS']
    dataframe = try_to_run(
        var='dataframe',
        code='conn = sql.connect(path)\
            \ndataframe = pd.read_sql(\
                f"SELECT *, rowid FROM {name}\
                    WHERE start_time >= {start} AND end_time <= {end}", conn)',
        error_check='',
        final_code='conn.close()',
        retries=retries,
        environment=locals())
    return not dataframe.empty, dataframe


def load_dataframe(name: str) -> tuple[bool, pd.DataFrame]:
    """
    Check if DataFrame is empty and
    creates DataFrame if file is non-existant.

    Returns:
        bool: True if dataframe is accessible and has data.
        pd.DataFrame: Accessed dataframe.
    """
    # Check if file does not exists
    path = os.path.join(cfg["WORKSPACE"], f'{cfg["DATA_PATH"]}{name}.db')
    dataframe = pd.DataFrame({})
    if not os.path.exists(path):
        return False, dataframe

    # Access database
    retries = cfg['RETRY_ATTEMPS']
    dataframe = try_to_run(
        var='dataframe',
        code='conn = sql.connect(path)\
            \ndataframe = pd.read_sql(f"SELECT *, rowid FROM {name}", conn)',
        error_check='',
        final_code='conn.close()',
        retries=retries,
        environment=locals())
    return not dataframe.empty, dataframe


def save_dataframe(dataframe: pd.DataFrame, name: str):
    """
    Saves dataframe .db file and handles errors.

    Args:
        dataframe (pd.DataFrame): Dataframe to be saved.
        path (str): Location the dataframe will be saved.
    """
    path = os.path.join(cfg["WORKSPACE"], f'{cfg["DATA_PATH"]}{name}.db')
    retries = cfg['RETRY_ATTEMPS']

    try_to_run(
        var='dataframe',
        code='conn = sql.connect(path)\
            \nconn.execute("BEGIN EXCLUSIVE")\
            \ndataframe.to_sql(\
                name, conn, if_exists="replace", index=False)',
        error_check='',
        final_code='conn.close()',
        retries=retries,
        environment=locals())


def load_input_time(name: str) -> int:
    """
    Will return the time of last input from path or return 0 if
    there were any mistakes in the process.

    Args:
        path (str): Path of last input dataframe.

    Returns:
        int: Time of latest input from path.
    """
    dataframe_is_loaded, device = load_lastest_row(name)
    recorded_time = 0
    if dataframe_is_loaded:
        recorded_time = device.iloc[0, 0]
    return recorded_time


def load_urls(
        path: str = cfg["URLS_PATH"]) -> tuple[bool, list[tuple[str, str]]]:
    """
    Access the URL file provided by the browser extension\
        and returns the values in a list.

    Args:
        path (str, optional): Path to URLS. Defaults to cfg["URLS_PATH"].

    Returns:
        bool: False if data has been retrieved.
        list[str]: List of URLs.
    """
    # Select the most recent file and remove all older files
    error, newest_file = clean_and_select_newest_url(path)
    if error:
        return True, []

    # Load the file and output list of URLs
    retries = cfg['RETRY_ATTEMPS']
    lines = try_to_run(
        var='lines',
        code='with open(newest_file, "r", encoding="utf-8") as file:\
            \n    lines = file.readlines()',
        error_check='',
        final_code='',
        retries=retries,
        environment=locals())

    # Separate the lines into a tuple containing title and URL.
    contents = []
    for line in lines:
        contents.append(tuple(line.strip().split("|-|")))
    return not contents, contents


def clean_and_select_newest_url(
        path: str = cfg["URLS_PATH"]) -> tuple[bool, str]:
    """
    Returns newest file name and removes the others

    Args:
        path (str, optional): Path to URLS. Defaults to cfg["URLS_PATH"].

    Returns:
        bool: If URLS path does not exist.
        str: File name.
    """
    # Check path exists
    if not os.path.exists(path):
        return True, ""

    path += "*.txt"
    files = glob.glob(path)
    newest_file = max(files, key=os.path.getmtime)  # getctime leads to errors

    threads = [
        Thread(target=os.remove, args=(file,))
        for file in files if file != newest_file]

    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except FileNotFoundError:
        pass
    return False, newest_file


def set_idle():
    """Function that sets all input databases to idle state."""
    time.sleep(1)
    now = int(time.time())
    idle_time = cfg["IDLE_TIME"]
    inputs = ["mouse", "keyboard", "audio", "fullscreen"]

    for input_name in inputs:
        input_dataframe = load_lastest_row(input_name)[1]
        if now - input_dataframe.loc[0, 'time'] < idle_time:
            input_dataframe.loc[0, 'time'] = now - idle_time
            modify_latest_row(input_name, input_dataframe, ['time'])


def send_notification(title: str, message: str, audio: str = "notification") -> None:
    """
    Sends a desktop notification with the title and message.

    Args:
        title (str): Title of the notification.
        message (str): Message of the notification.
        audio (str): Desired audio to play.
    """
    notification = cfg["NOTIFICATION"]
    notification.title = title
    notification.message = message
    notification.audio = os.path.join(
        cfg["WORKSPACE"], "assets", audio + ".wav")
    notification.send(block=False)
