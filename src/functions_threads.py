"""
Creates event listeners that will be used to detect if the user
is not idle. If the user is not idle, update data file.
"""
# pylint: disable=unused-variable, bare-except, broad-exception-caught
# pylint: disable=too-few-public-methods, import-error
# flake8: noqa: F401
import time
import os
import sys
import logging
import shutil
from typing import Any
from datetime import datetime, timedelta
from flask import request, jsonify, Flask
import soundcard as sc
import pandas as pd
from pynput import keyboard
from pyautogui import position
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, callback
from functions_activity import parser, secondary_parser
from helper_io import save_dataframe, load_config, retry
from pages import layout_dashboard, layout_activity, layout_categories, \
    layout_inputs, layout_credits, layout_configuration, \
    layout_configuration2, layout_urls, layout_milestones, \
    layout_trends, layout_all, layout_conflicts, layout_flashcards


@retry(attempts=2, wait=1.0)
def mouse_idle_detector() -> None:
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


@retry(attempts=2, wait=1.0)
def keyboard_idle_detector() -> None:
    """
    Detects if keyboard had activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    def track_activity(*_args: Any) -> None:
        save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'keyboard')

    while True:
        cfg = load_config()
        with keyboard.Listener(on_press=track_activity) as listener:
            listener.join()
        time.sleep(cfg['IDLE_CHECK_INTERVAL'])


@retry(attempts=2, wait=1.0)
def activity_detector() -> None:
    """
    Detects window activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    while True:
        cfg = load_config()
        parser()
        time.sleep(cfg['ACTIVITY_CHECK_INTERVAL'])


@retry(attempts=2, wait=1.0)
def activity_processor() -> None:
    """
    Process activity database into categories and total databases.
    """
    while True:
        cfg = load_config()
        secondary_parser()
        time.sleep(cfg['PARTIAL_CATEGORIES_INTERVAL'])


@retry(attempts=2, wait=1.0)
def audio_idle_detector() -> None:
    """
    Detects if audio had activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    while True:
        cfg = load_config()
        with sc.get_microphone(
            id=str(sc.default_speaker().name), include_loopback=True
        ).recorder(samplerate=148000) as mic:
            data = mic.record(numframes=10000)
            time.sleep(1)
        if any(x.any() != 0 for x in data):
            save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'audio')
        time.sleep(cfg['IDLE_CHECK_INTERVAL'])


@retry(attempts=2, wait=1.0)
def backups() -> None:
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
    print(f"\033[96m{time.strftime('%X')} Backend: " +
            f"Backup {now.strftime(date_format)} done successfully\033[00m")

    # Delete oldest backup if there are more backups than desired
    files = os.listdir(cfg["BACKUP"])
    files.sort()
    while cfg["NUMBER_OF_BACKUPS"] < len(files):
        os.remove(os.path.join(cfg["BACKUP"], files[0]))
        files = os.listdir(cfg["BACKUP"])
        files.sort()


@retry(attempts=2, wait=1.0)
def auxiliary_work() -> None:
    """
    Does auxiliary work for the program.
    Backup.
    """
    while True:
        cfg = load_config()
        time.sleep(cfg["IDLE_CHECK_INTERVAL"])
        backups()


def server_supervisor() -> None:
    """Server runner function."""
    external_stylesheets = [dbc.themes.BOOTSTRAP]
    app = Dash(
        __name__,
        update_title="Productivity Dashboard...",
        external_stylesheets=external_stylesheets,
        title="Productivity Dashboard",
        assets_folder='../assets')

    server = app.server
    assert isinstance(server, Flask)

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
            case "/flashcards":
                layout = layout_flashcards.layout
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

    # Use the extension GET requests to create the URLS database
    class HideSpecificGetRequest(logging.Filter):
        """Hides GET requests from extension (too long)."""
        def filter(self, record):
            return "/urldata/" not in record.getMessage()

    log.addFilter(HideSpecificGetRequest())

    @server.route('/urldata/', methods=['GET'])
    def extension_handler():
        titles = request.args.get('titles')
        assert isinstance(titles, str)
        titles = titles.split("|-|")
        titles = [  # Correct for special characters
            title.encode("utf-8").decode("unicode_escape")
            for title in titles
        ]

        urls = request.args.get("urls")
        assert isinstance(urls, str)
        urls = urls.split("|-|")

        if len(titles) != len(urls):
            print("\033[93mTitles and urls list must have same length\033[00m")
            sys.exit()

        dataframe = pd.DataFrame({'title': titles, 'url': urls})
        save_dataframe(dataframe, "urls")
        return jsonify({'message': 'OK'}), 200

    # Run the server
    server.run(port=8050)
