"""
Study advisor, sends realtime messages to support user.
"""
# pylint: disable=global-variable-not-assigned
import time
from datetime import datetime, timedelta
import pandas as pd
from helper_io import load_config, send_notification, load_day_total, \
    load_dataframe, save_dataframe, check_dataframe


MESSAGES = {}
TITLES = {}


def load_messages():
    """
    Loads messages to be used in the notifications
    """
    global MESSAGES, TITLES
    cfg = load_config()
    work_goal = cfg["WORK_DAILY_GOAL"]

    message = "Passed your personal daily limit. "
    message += "Consider studying more!"
    MESSAGES["personal"] = message
    TITLES["personal"] = "❌ Misstep detected! ❌"

    message = "Completed the small daily study goal. "
    message += "Congratulations for your consistency!"
    MESSAGES["small_work"] = message
    TITLES["small_work"] = "💡 Progress made! 💡"

    message = "Completed 25% of the daily study goal. "
    message += f"Consider studying {int(work_goal * 60 * 0.75)}m "
    message += "to stay on track!"
    MESSAGES["work_25"] = message
    TITLES["work_25"] = "💡 Progress made! 💡"

    message = "Completed 50% of the daily study goal. "
    message += f"Consider studying {int(work_goal * 60 * 0.50)}m "
    message += "to stay on track!"
    MESSAGES["work_50"] = message
    TITLES["work_50"] = "💡 Progress made! 💡"

    message = "Completed 75% of the daily study goal. "
    message += f"Consider studying {int(work_goal * 60 * 0.25)}m "
    message += "to stay on track!"
    MESSAGES["work_75"] = message
    TITLES["work_75"] = "💡 Progress made! 💡"

    message = "Completed 100% of the daily study goal. "
    message += "Congratulations! +1 streak point"
    MESSAGES["work_100"] = message
    TITLES["work_100"] = "🎉 Milestone achieved! 🎉"


def fix_milestones() -> pd.DataFrame:
    """
    Fixes milestone database in case of: non-existance, updated goals.

    Returns:
        pd.DataFrame: Correct milestones dataframe.
    """
    cfg = load_config()
    day = datetime.utcfromtimestamp(int(time.time()))
    day += timedelta(hours=cfg["GMT_OFFSET"])
    day = day.strftime('%Y-%m-%d')
    dataframe = pd.DataFrame({
        'day': [day],
        'work_100': [0],
        'work_75': [0],
        'work_50': [0],
        'work_25': [0],
        'small_work': [0],
        'personal': [0]
    })

    # Check existance
    if not check_dataframe("milestones"):
        save_dataframe(dataframe, "milestones")

    milestones = load_dataframe("milestones").drop("rowid", axis=1)

    # Check day change
    if milestones.loc[0, "day"] != day:
        milestones = dataframe
        save_dataframe(dataframe, "milestones")

    # Check columns
    if not milestones.columns.equals(dataframe.columns):
        milestones = dataframe
        save_dataframe(dataframe, "milestones")
    return milestones


def check_milestones():
    """
    Function to check for goal milestones.
    Sends a desktop notification when milestone is achieved.
    """
    global MESSAGES, TITLES
    cfg = load_config()
    data = load_day_total(364)
    milestones = fix_milestones()
    personal_done = data.loc[0, "Personal"]
    work_done = data.loc[0, "Work"]
    work_goal = cfg["WORK_DAILY_GOAL"]
    notification = f"\033[96m{time.strftime('%X')} Notification:"

    # Check personal
    if not milestones.loc[0, "personal"]:
        if personal_done >= max(
            cfg["PERSONAL_DAILY_GOAL"],
            work_done * cfg["WORK_TO_PERSONAL_MULTIPLIER"]
        ):
            milestones.loc[0, "personal"] = 1
            print(notification, "personal\033[00m")
            send_notification(
                TITLES["personal"], MESSAGES["personal"], "bad")

    # Check work
    if not milestones.loc[0, "small_work"]:
        if work_done >= cfg["SMALL_WORK_DAILY_GOAL"]:
            milestones.loc[0, "small_work"] = 1
            print(notification, "small_work\033[00m")
            send_notification(
                TITLES["small_work"], MESSAGES["small_work"], "neutral")

    if not milestones.loc[0, "work_25"]:
        if work_done >= work_goal * 0.25:
            milestones.loc[0, "work_25"] = 1
            print(notification, "work_25\033[00m")
            send_notification(
                TITLES["work_25"], MESSAGES["work_25"], "neutral")

    if not milestones.loc[0, "work_50"]:
        if work_done >= work_goal * 0.50:
            milestones.loc[0, "work_50"] = 1
            print(notification, "work_50\033[00m")
            send_notification(
                TITLES["work_50"], MESSAGES["work_50"], "neutral")

    if not milestones.loc[0, "work_75"]:
        if work_done >= work_goal * 0.75:
            milestones.loc[0, "work_75"] = 1
            print(notification, "work_75\033[00m")
            send_notification(
                TITLES["work_75"], MESSAGES["work_75"], "neutral")

    if not milestones.loc[0, "work_100"]:
        if work_done >= work_goal:
            milestones.loc[0, "work_100"] = 1
            print(notification, "work_100\033[00m")
            send_notification(
                TITLES["work_100"], MESSAGES["work_100"], "good")

    # Update milestones dataframe
    save_dataframe(milestones, "milestones")
    time.sleep(5)


def study_advisor():
    """
    Main study advisor functions that coordinates all functionality.
    """
    while True:
        cfg = load_config()
        load_messages()
        check_milestones()

        time.sleep(cfg["ADVISOR_CHECK_INTERVAL"])
