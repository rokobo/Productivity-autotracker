"""
Creates event listeners that will be used to detect if the user
is not idle. If the user is not idle, update data file.
"""
# pylint: disable=unused-variable, bare-except
# flake8: noqa: F401
import time
import struct
import logging
import pyaudiowpatch as pyaudio
import pandas as pd
from pynput import keyboard
from pyautogui import position
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, callback
from functions_activity import parser
from pages import layout_dashboard, layout_activity, layout_categories, \
    layout_inputs, layout_credits, layout_configuration, \
    layout_configuration2, layout_goals
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


def detect_audio():
    """Save idle time if audio detected."""
    with pyaudio.PyAudio() as audio:
        # Get speaker info
        wasapi_info = audio.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = audio.get_device_info_by_index(
            wasapi_info["defaultOutputDevice"])

        if not default_speakers["isLoopbackDevice"]:
            for loopback in audio.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                raise OSError("No device, run `python -m pyaudiowpatch`")

        def stream_callback(in_data, _frame_count, _time_info, _status):
            """Check audio intensity and save input detection if needed."""
            intensity = max(
                abs(sample) for sample
                in struct.unpack(f"<{len(in_data) // 2}h", in_data))
            if intensity > 1:
                save_dataframe(
                    pd.DataFrame({'time': [int(time.time())]}), 'audio')
                return (in_data, pyaudio.paAbort)
            return (in_data, pyaudio.paContinue)

        with audio.open(
            format=pyaudio.paInt24,
            channels=default_speakers["maxInputChannels"],
            rate=int(default_speakers["defaultSampleRate"]),
            frames_per_buffer=pyaudio.get_sample_size(pyaudio.paInt24),
            input=True,
            input_device_index=default_speakers["index"],
            stream_callback=stream_callback
        ) as stream:
            time.sleep(1)

def audio_idle_detector():
    """
    Detects if audio had activity. Waits a couple of seconds
    after detection to actively look for activity again.
    """
    while True:
        cfg = load_config()
        try:
            detect_audio()
        except:
            print("Audio idle detector error")
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
            case _:
                layout = layout_dashboard.layout
        return layout

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    server.run(host="0.0.0.0", port="8050")
    while True:
        time.sleep(5)
