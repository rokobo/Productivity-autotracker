"""
Main runner file for the Dash app and its background processes.
"""
import threading
import time
from helper_io import load_input_time, load_config
from functions_threads import mouse_idle_detector, keyboard_idle_detector, \
    activity_detector, audio_idle_detector, server_supervisor


if __name__ == '__main__':
    while True:
        try:
            # Background detection threads
            mouse_thread = threading.Thread(target=mouse_idle_detector)
            mouse_thread.daemon = True
            mouse_thread.start()

            keyboard_thread = threading.Thread(target=keyboard_idle_detector)
            keyboard_thread.daemon = True
            keyboard_thread.start()

            audio_thread = threading.Thread(target=audio_idle_detector)
            audio_thread.daemon = True
            audio_thread.start()

            activity_thread = threading.Thread(target=activity_detector)
            activity_thread.daemon = True
            activity_thread.start()

            # Dash server thread
            server_thread = threading.Thread(target=server_supervisor)
            server_thread.daemon = True
            server_thread.start()

            cfg = load_config()
            threshold = cfg['UNRESPONSIVE_THRESHOLD']
            time.sleep(cfg['IDLE_CHECK_INTERVAL'] * 5)

            # Restart all threads if server is unresponsive
            while (int(time.time()) - load_input_time('backend')) < threshold:
                time.sleep(3)
            raise RuntimeError

        except RuntimeError:
            print("MAIN PROGRAM FAILURE, RESTARTING...")
            time.sleep(3)
