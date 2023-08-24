"""
Creates event listeners that will be used to detect if the user
is not idle. If the user is not idle, update data file.
"""
# pylint: disable=unused-variable, bare-except, broad-exception-caught
# flake8: noqa: F401
import time
import logging
from flask import request
import soundcard as sc
import pandas as pd
from pynput import keyboard
from pyautogui import position
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, callback
from functions_activity import parser
from helper_io import save_dataframe, load_config
from pages import layout_dashboard, layout_activity, layout_categories, \
    layout_inputs, layout_credits, layout_configuration, \
    layout_configuration2, layout_goals, layout_urls


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
            case "/goals":
                layout = layout_goals.layout
            case "/urls":
                layout = layout_urls.layout
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

    server.run(host="0.0.0.0", port="8050")
