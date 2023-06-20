"""
Creates event listeners that will be used to detect if the user
is not idle. If the user is not idle, update data file.
"""
import time
import asyncio
import logging
import pandas as pd
from pynput import keyboard
import winsdk.windows.media.control as wmc
from pyautogui import position
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, callback
from functions_activity import parser
from pages import layout_dashboard, layout_activity, layout_categories, \
    layout_inputs, layout_credits, layout_configuration
from helper_io import save_dataframe, load_config


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
            save_dataframe(
                pd.DataFrame({'time': [int(time.time())]}), 'mouse')
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


async def is_media_running() -> bool:
    """
    Checks if the media is playing.

    Returns:
        bool: True if the media playback status matches "PLAYING".
    """
    sessions = await (
        wmc.GlobalSystemMediaTransportControlsSessionManager.request_async())
    session = sessions.get_current_session()
    if session is None:
        return False
    state = "PLAYING"
    expected_status = int(
        wmc.GlobalSystemMediaTransportControlsSessionPlaybackStatus[state])
    current_status = session.get_playback_info().playback_status
    return expected_status == current_status


def audio_idle_detector():
    """
    Detects if audio had activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    while True:
        cfg = load_config()
        if asyncio.run(is_media_running()):
            save_dataframe(
                pd.DataFrame({'time': [int(time.time())]}), 'audio')
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
        if pathname == "/activity":
            return layout_activity.layout
        if pathname == "/categories":
            return layout_categories.layout
        if pathname == "/inputs":
            return layout_inputs.layout
        if pathname == "/credits":
            return layout_credits.layout
        if pathname == "/configuration":
            return layout_configuration.layout
        return layout_dashboard.layout

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    server.run(host="0.0.0.0", port="8050")
    while True:
        time.sleep(5)
