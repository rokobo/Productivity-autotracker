"""
Creates event listeners that will be used to detect if the user
is not idle. If the user is not idle, update data file.
"""
# pylint: disable=unused-variable, bare-except, broad-exception-caught
# pylint: disable=too-few-public-methods
# flake8: noqa: F401
import time
import os
import logging
import shutil
from datetime import datetime, timedelta
from flask import request
import soundcard as sc
import pandas as pd
from pynput import keyboard
from pyautogui import position
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, callback
from functions_activity import parser
from helper_io import save_dataframe, load_config, load_dataframe, \
    load_day_total, append_to_database, delete_from_dataframe
from pages import layout_dashboard, layout_activity, layout_categories, \
    layout_inputs, layout_credits, layout_configuration, \
    layout_configuration2, layout_goals, layout_urls, layout_milestones, \
    layout_trends, layout_all, layout_breaks, layout_conflicts


def mouse_idle_detector():
    """
    Detects if mouse had activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    last_position = position()
    while True:
        cfg = load_config()
        new_position = position()
        if new_position != last_position:
            save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'mouse')
            last_position = new_position
        time.sleep(cfg['IDLE_CHECK_INTERVAL'])


def keyboard_idle_detector():
    """
    Detects if keyboard had activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    def track_activity(*_args):
        save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'keyboard')
        return False
    while True:
        cfg = load_config()
        with keyboard.Listener(on_press=track_activity) as listener:
            listener.join()
        time.sleep(cfg['IDLE_CHECK_INTERVAL'])


def activity_detector():
    """
    Detects window activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    while True:
        cfg = load_config()
        parser()
        time.sleep(cfg['ACTIVITY_CHECK_INTERVAL'])


def audio_idle_detector():
    """
    Detects if audio had activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    while True:
        cfg = load_config()
        with sc.get_microphone(
            id=str(sc.default_speaker().name), include_loopback=True
        ).recorder(samplerate=48000) as mic:
            data = mic.record(10)
        if any(x.any() != 0 for x in data):
            save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'audio')
        time.sleep(cfg['IDLE_CHECK_INTERVAL'])


def backups():
    """
    Does backup for the activity database, which is the one
    that generates all other databases.
    """
    cfg = load_config()
    need_backup = False
    now = datetime.now()
    date_format = "%Y-%m-%d-%H-%M"

    # Check if folder exists
    if not os.path.exists(cfg["BACKUP"]):
        os.makedirs(cfg["BACKUP"])

    # Check if backup is needed
    files = os.listdir(cfg["BACKUP"])
    files.sort()
    if not files:
        need_backup = True
    else:
        last_backup = now - datetime.strptime(files[-1][:-3], date_format)
        if last_backup > timedelta(minutes=cfg["BACKUP_INTERVAL"]):
            need_backup = True

    if not need_backup:
        return

    # Copy activity database to backup folder
    src = os.path.join(cfg["WORKSPACE"], 'data/activity.db')
    dest = os.path.join(cfg["BACKUP"], f'{now.strftime(date_format)}.db')
    shutil.copy2(src, dest)

    # Delete oldest backup if there are more backups than desired
    files = os.listdir(cfg["BACKUP"])
    files.sort()
    while cfg["NUMBER_OF_BACKUPS"] < len(files):
        os.remove(os.path.join(cfg["BACKUP"], files[0]))
        files = os.listdir(cfg["BACKUP"])
        files.sort()


def break_days():
    """
    Adds break event to break days.
    """
    cfg = load_config()
    breaks = load_dataframe("breaks", True)
    date_format = "%Y-%m-%d"
    if breaks.empty:
        return
    for day in breaks["day"].to_list():
        start = datetime.strptime(day, date_format)
        time_difference = datetime.now().date() - start.date()
        if time_difference.days <= 0:
            continue
        start = int(start.timestamp() + 1)
        work_done = load_day_total(364 - time_difference.days).loc[0, "Work"]
        if work_done >= cfg["WORK_DAILY_GOAL"]:
            delete_from_dataframe("breaks", "day", [day])
            continue
        end = int(start + ((cfg["WORK_DAILY_GOAL"] - work_done) * 3600))
        new_row = pd.DataFrame({
            'start_time': [start], 'end_time': [end], 'app': ["BREAK TIME"],
            'info': [""], 'handle': [-1], 'pid': [-1],
            'process_name': ["BREAK TIME"], 'url': [""], 'domain': [""]
        })
        append_to_database("activity", new_row)
        delete_from_dataframe("breaks", "day", [day])
        print("\033[96mAuxiliary notification: " +
            f"Break day {day} added successfully to event database\033[00m")


def auxiliary_work():
    """
    Does auxiliary work for the program.
    Backup, break days.
    """
    while True:
        cfg = load_config()
        time.sleep(cfg["IDLE_CHECK_INTERVAL"])
        backups()
        break_days()


def server_supervisor():
    """Server runner function."""
    external_stylesheets = [dbc.themes.BOOTSTRAP]
    app = Dash(
        __name__,
        update_title=None,
        external_stylesheets=external_stylesheets,
        title="Productivity Dashboard",
        assets_folder='../assets')

    server = app.server

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    @callback(
        Output('page-content', 'children'),
        Input('url', 'pathname'))
    def display_page(pathname):
        """Support for multi-page Dash website."""
        match pathname:
            case "/activity":
                layout = layout_activity.layout
            case "/categories":
                layout = layout_categories.layout
            case "/inputs":
                layout = layout_inputs.layout
            case "/credits":
                layout = layout_credits.layout
            case "/configuration":
                layout = layout_configuration.layout
            case "/configuration2":
                layout = layout_configuration2.layout
            case "/breaks":
                layout = layout_breaks.layout
            case "/goals":
                layout = layout_goals.layout
            case "/trends":
                layout = layout_trends.layout
            case "/all":
                layout = layout_all.layout
            case "/urls":
                layout = layout_urls.layout
            case "/milestones":
                layout = layout_milestones.layout
            case "/conflicts":
                layout = layout_conflicts.layout
            case _:
                layout = layout_dashboard.layout
        return layout

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)

    class HideSpecificGetRequest(logging.Filter):
        """Hides GET requests from extension (too long)."""
        def filter(self, record):
            return "/urldata/" not in record.getMessage()

    log.addFilter(HideSpecificGetRequest())

    @server.route('/urldata/', methods=['GET'])
    def extension_handler():
        titles = request.args.get('titles').split("|-|")
        urls = request.args.get("urls").split("|-|")
        if len(titles) != len(urls):
            raise ValueError("Titles and urls list must have same length")
        dataframe = pd.DataFrame({'title': titles, 'url': urls})
        save_dataframe(dataframe, "urls")
        return "OK"

    server.run(port="8050")
