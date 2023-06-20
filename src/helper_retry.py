"""Function for trying to execute code."""
# pylint: disable=exec-used, eval-used, broad-exception-caught
# pylint: disable=unused-import, too-many-arguments, no-name-in-module
# flake8: noqa: F401
import os
import time
import sqlite3 as sql
import yaml
import pandas as pd
from win32com.client import GetObject
from win32gui import GetForegroundWindow
from psutil import process_iter, Process


def try_to_run(var: str, code: str, error_check: str, final_code: str,
        retries: int, environment: dict) -> any:
    """
    Tries to run a block of code a few times, until it passes the error
    check or the number of tries is exceeded. On success, it returns the
    variable with the name passed in var.

    Observations:
        Remember to import all external libraries in this function's file.

    Args:
        var (str): Name of variable to be retrived after code block execution.
        code (str): Block of code to be executed.
        error_check (str): Code that evaluates to True if error is detected.
        final_code (str): Code that is executed after block of code attempt.
        retries (int): Number of times the code is tried to run.
        environment (dict): Local variables to be used in exec and eval.

    Returns:
        any: Value of the retrieved variable or None if no var.
    """
    if error_check == "":
        error_check = "False"
    tries = 0
    while tries < retries:
        try:
            # Execute code block and verify success
            exec(code, globals(), environment)
            if eval(error_check, globals(), environment):
                raise ValueError
            break
        except Exception:
            tries += 1
            time.sleep(0.01)
        finally:
            exec(final_code, globals(), environment)

    # Final verification
    if eval(error_check, globals(), environment):
        raise ValueError(f"Error in '{code}' after {tries} tries ({0.01 * tries}s)")

    # Retrieve desired variable (if specified)
    if var != "":
        return environment[var]
    return None
