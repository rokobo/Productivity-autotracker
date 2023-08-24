"""
Main runner file for the Dash app and its background processes.
"""
# pylint: disable=broad-exception-caught
from threading import Thread
from multiprocessing import Process
import time
from helper_io import load_input_time, load_config
from functions_threads import mouse_idle_detector, keyboard_idle_detector, \
    activity_detector, audio_idle_detector, server_supervisor
from study_advisor import study_advisor


CFG = load_config()
THRESHOLD = CFG['UNRESPONSIVE_THRESHOLD']


def is_backend_online():
    """Determines if backend has been updated in a given timeframe."""
    return (int(time.time()) - load_input_time('backend')) < THRESHOLD


if __name__ == '__main__':
    while True:
        try:
            # Background detection threads
            mouse_thread = Thread(target=mouse_idle_detector)
            mouse_thread.daemon = True
            mouse_thread.start()

            keyboard_thread = Thread(target=keyboard_idle_detector)
            keyboard_thread.daemon = True
            keyboard_thread.start()

            # Soundcard library cannot run in thread
            audio_thread = Process(target=audio_idle_detector)
            audio_thread.daemon = True
            audio_thread.start()

            # Main activity process
            activity_thread = Process(target=activity_detector)
            activity_thread.daemon = True
            activity_thread.start()

            # Dash server process
            server_thread = Process(target=server_supervisor)
            server_thread.daemon = True
            server_thread.start()

            # Study advisor process
            advisor_thread = Process(target=study_advisor)
            advisor_thread.daemon = True
            advisor_thread.start()

            time.sleep(CFG['IDLE_CHECK_INTERVAL'] * 5)

            # Restart all threads if backend or threads are unresponsive
            ARE_THREADS_ONLINE = True
            while is_backend_online() and ARE_THREADS_ONLINE:
                ARE_THREADS_ONLINE = mouse_thread.is_alive()
                ARE_THREADS_ONLINE &= keyboard_thread.is_alive()
                ARE_THREADS_ONLINE &= audio_thread.is_alive()
                ARE_THREADS_ONLINE &= activity_thread.is_alive()
                ARE_THREADS_ONLINE &= server_thread.is_alive()
                ARE_THREADS_ONLINE &= advisor_thread.is_alive()
                time.sleep(3)
            raise RuntimeError

        except RuntimeError:
            print("MAIN PROGRAM FAILURE, RESTARTING...")
            time.sleep(3)
        except Exception:  # For other possible thread errors
            print("General error caught")
