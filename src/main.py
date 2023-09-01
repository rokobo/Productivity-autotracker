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
    activity_detector, audio_idle_detector, server_supervisor#, backups
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
                print("Problem in activity_process, restarting process...")
                activity_process = Process(target=activity_detector)
                activity_process.daemon = True
                activity_process.start()

            try:  # Mouse detection thread
                assert mouse_thread.is_alive()
            except Exception:
                print("Problem in mouse_thread, restarting thread...")
                mouse_thread = Thread(target=mouse_idle_detector)
                mouse_thread.daemon = True
                mouse_thread.start()

            try:  # Keyboard detection thread
                assert keyboard_thread.is_alive()
            except Exception:
                print("Problem in keyboard_thread, restarting thread...")
                keyboard_thread = Thread(target=keyboard_idle_detector)
                keyboard_thread.daemon = True
                keyboard_thread.start()

            try:  # Soundcard library cannot run in thread
                assert audio_process.is_alive()
            except Exception:
                print("Problem in audio_process, restarting process...")
                audio_process = Process(target=audio_idle_detector)
                audio_process.daemon = True
                audio_process.start()

            try:  # Study advisor process
                assert advisor_process.is_alive()
            except Exception:
                print("Problem in advisor_process, restarting process...")
                advisor_process = Process(target=study_advisor)
                advisor_process.daemon = True
                advisor_process.start()

            try:  # Dash server process
                assert server_process.is_alive()
            except Exception:
                print("Problem in server_process, restarting process...")
                server_process = Process(target=server_supervisor)
                server_process.daemon = True
                server_process.start()

            # try:  # Backup process TODO
            #     assert backup_process.is_alive()
            # except Exception:
            #     print("Problem in backup_process, restarting process...")
            #     backup_process = Process(target=backups)
            #     backup_process.daemon = True
            #     backup_process.start()

            time.sleep(CFG['IDLE_CHECK_INTERVAL'] * 5)

        except Exception:
            print("MAIN PROGRAM FAILURE, RESTARTING...")
