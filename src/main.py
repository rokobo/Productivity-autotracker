"""
Main runner file for the Dash app and its background processes.
"""
# pylint: disable=broad-exception-caught, used-before-assignment, import-error
# flake8: noqa: F821
from threading import Thread
from multiprocessing import Process
import time
from helper_io import load_input_time, load_config, start_databases, \
    send_notification
from functions_threads import (
    mouse_idle_detector,
    keyboard_idle_detector,
    activity_detector,
    activity_processor,
    audio_idle_detector,
    server_supervisor,
    auxiliary_work,
)
from study_advisor import study_advisor


CFG = load_config()
THRESHOLD = CFG["UNRESPONSIVE_THRESHOLD"]
start_databases()


def did_backend_update_recently():
    """Determines if backend has been updated in a given timeframe."""
    since = (int(time.time()) - load_input_time("backend"))
    if since > 300:
        send_notification(
            "Backend error, manually intervene",
            "More than 5 minutes since last backend update!",
            "bad"
        )
    return since < THRESHOLD


if __name__ == "__main__":
    # Initialize processes and threads
    activity_process = Process(target=activity_detector)
    activity_process.daemon = True
    activity_process.start()
    print(f"\033[92m{time.strftime('%X')} activity_process started!\033[00m")

    activity_process2 = Thread(target=activity_processor)
    activity_process2.daemon = True
    activity_process2.start()
    print(f"\033[92m{time.strftime('%X')} activity_process2 started!\033[00m")

    mouse_thread = Thread(target=mouse_idle_detector)
    mouse_thread.daemon = True
    mouse_thread.start()
    print(f"\033[92m{time.strftime('%X')} mouse_thread started!\033[00m")

    keyboard_thread = Thread(target=keyboard_idle_detector)
    keyboard_thread.daemon = True
    keyboard_thread.start()
    print(f"\033[92m{time.strftime('%X')} keyboard_thread started!\033[00m")

    audio_process = Thread(target=audio_idle_detector)
    audio_process.daemon = True
    audio_process.start()
    print(f"\033[92m{time.strftime('%X')} audio_process started!\033[00m")

    advisor_process = Process(target=study_advisor)
    advisor_process.daemon = True
    advisor_process.start()
    print(f"\033[92m{time.strftime('%X')} advisor_process started!\033[00m")

    auxiliary_process = Process(target=auxiliary_work)
    auxiliary_process.daemon = True
    auxiliary_process.start()
    print(f"\033[92m{time.strftime('%X')} auxiliary_process started!\033[00m")

    server_process = Process(target=server_supervisor)
    server_process.daemon = True
    server_process.start()
    print(f"\033[92m{time.strftime('%X')} server_process started!\033[00m")

    # Restart mechanism
    while True:
        try:
            # Main activity process
            if not activity_process.is_alive():
                activity_process.terminate()
                activity_process.join()
                print(
                    f"\033[91m{time.strftime('%X')} Error in",
                    "activity_process... \033[00m ",
                    end="",
                )
                activity_process = Process(target=activity_detector)
                activity_process.daemon = True
                activity_process.start()
                print("\033[92mRestarted!\033[00m")

            # Secondary activity thread
            if not activity_process2.is_alive():
                print(
                    f"\033[91m{time.strftime('%X')} Error in",
                    "activity_process2... \033[00m",
                    end="",
                )
                activity_process2 = Thread(target=activity_processor)
                activity_process2.daemon = True
                activity_process2.start()
                print("\033[92mRestarted!\033[00m")

            # Mouse detection thread
            if not mouse_thread.is_alive():
                print(
                    f"\033[91m{time.strftime('%X')} Error in",
                    "mouse_thread... \033[00m",
                    end="",
                )
                mouse_thread = Thread(target=mouse_idle_detector)
                mouse_thread.daemon = True
                mouse_thread.start()
                print("\033[92mRestarted!\033[00m")

            # Keyboard detection thread
            if not keyboard_thread.is_alive():
                print(
                    f"\033[91m{time.strftime('%X')} Error in",
                    "keyboard_thread... \033[00m",
                    end="",
                )
                keyboard_thread = Thread(target=keyboard_idle_detector)
                keyboard_thread.daemon = True
                keyboard_thread.start()
                print("\033[92mRestarted!\033[00m")

            # Audio detection thread
            if not audio_process.is_alive():
                print(
                    f"\033[91m{time.strftime('%X')} Error in",
                    "audio_process... \033[00m",
                    end="",
                )
                audio_process = Thread(target=audio_idle_detector)
                audio_process.daemon = True
                audio_process.start()
                print("\033[92mRestarted!\033[00m")

            # Study advisor process
            if not advisor_process.is_alive():
                print(
                    f"\033[91m{time.strftime('%X')} Error in",
                    "advisor_process... \033[00m",
                    end="",
                )
                advisor_process = Process(target=study_advisor)
                advisor_process.daemon = True
                advisor_process.start()
                print("\033[92mRestarted!\033[00m")

            # Dash server process
            if not server_process.is_alive():
                print(
                    f"\033[91m{time.strftime('%X')} Error in",
                    "server_process... \033[00m",
                    end="",
                )
                server_process = Process(target=server_supervisor)
                server_process.daemon = True
                server_process.start()
                print("\033[92mRestarted!\033[00m")

            # Backup process
            if not auxiliary_process.is_alive():
                print(
                    f"\033[91m{time.strftime('%X')} Error in",
                    "auxiliary_process... \033[00m",
                    end="",
                )
                auxiliary_process = Process(target=auxiliary_work)
                auxiliary_process.daemon = True
                auxiliary_process.start()
                print("\033[92mRestarted!\033[00m")

            time.sleep(CFG["IDLE_CHECK_INTERVAL"] * 5)
            if not did_backend_update_recently():
                raise RuntimeError

        except Exception:
            print(
                f"\033[101m{time.strftime('%X')}",
                "MAIN PROGRAM FAILURE, RESTARTING...\033[00m",
            )
