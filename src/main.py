"""
Main runner file for the Dash app and its background processes.
"""
# pylint: disable=broad-exception-caught, used-before-assignment, import-error
# flake8: noqa: F821
from threading import Thread
from multiprocessing import Process
import time
from helper_io import load_input_time, load_config
from functions_threads import mouse_idle_detector, keyboard_idle_detector, \
    activity_detector, audio_idle_detector, server_supervisor, auxiliary_work
from study_advisor import study_advisor


CFG = load_config()
THRESHOLD = CFG['UNRESPONSIVE_THRESHOLD']


def did_backend_update_recently():
    """Determines if backend has been updated in a given timeframe."""
    return (int(time.time()) - load_input_time('backend')) < THRESHOLD


if __name__ == '__main__':
    while True:
        try:
            try:  # Main activity process
                assert activity_process.is_alive()
                assert did_backend_update_recently()
            except Exception:
                print(f"\033[91m{time.strftime('%X')} Error in",
                    "activity_process... \033[00m ", end="")
                activity_process = Process(target=activity_detector)
                activity_process.daemon = True
                activity_process.start()
                print("\033[92mRestarted!\033[00m")

            try:  # Mouse detection thread
                assert mouse_thread.is_alive()
            except Exception:
                print(f"\033[91m{time.strftime('%X')} Error in",
                    "mouse_thread... \033[00m", end="")
                mouse_thread = Thread(target=mouse_idle_detector)
                mouse_thread.daemon = True
                mouse_thread.start()
                print("\033[92mRestarted!\033[00m")

            try:  # Keyboard detection thread
                assert keyboard_thread.is_alive()
            except Exception:
                print(f"\033[91m{time.strftime('%X')} Error in",
                    "keyboard_thread... \033[00m", end="")
                keyboard_thread = Thread(target=keyboard_idle_detector)
                keyboard_thread.daemon = True
                keyboard_thread.start()
                print("\033[92mRestarted!\033[00m")

            try:  # Audio detection thread
                assert audio_process.is_alive()
            except Exception:
                print(f"\033[91m{time.strftime('%X')} Error in",
                    "audio_process... \033[00m", end="")
                audio_process = Thread(target=audio_idle_detector)
                audio_process.daemon = True
                audio_process.start()
                print("\033[92mRestarted!\033[00m")

            try:  # Study advisor process
                assert advisor_process.is_alive()
            except Exception:
                print(f"\033[91m{time.strftime('%X')} Error in",
                    "advisor_process... \033[00m", end="")
                advisor_process = Process(target=study_advisor)
                advisor_process.daemon = True
                advisor_process.start()
                print("\033[92mRestarted!\033[00m")

            try:  # Dash server process
                assert server_process.is_alive()
            except Exception:
                print(f"\033[91m{time.strftime('%X')} Error in",
                    "server_process... \033[00m", end="")
                server_process = Process(target=server_supervisor)
                server_process.daemon = True
                server_process.start()
                print("\033[92mRestarted!\033[00m")

            try:  # Backup process
                assert auxiliary_process.is_alive()
            except Exception:
                print(f"\033[91m{time.strftime('%X')} Error in",
                    "auxiliary_process... \033[00m", end="")
                auxiliary_process = Process(target=auxiliary_work)
                auxiliary_process.daemon = True
                auxiliary_process.start()
                print("\033[92mRestarted!\033[00m")

            time.sleep(CFG['IDLE_CHECK_INTERVAL'] * 5)

        except Exception:
            print(f"\033[101m{time.strftime('%X')}",
                "MAIN PROGRAM FAILURE, RESTARTING...\033[00m")
