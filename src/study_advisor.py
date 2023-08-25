"""
Study advisor, sends realtime messages to support user.
"""
import time
from datetime import datetime, timedelta
import pandas as pd
from helper_io import load_config, send_notification, load_day_total, \
    load_dataframe, save_dataframe, check_dataframe


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
        'work_100': [False],
        'work_75': [False],
        'work_50': [False],
        'work_25': [False],
        'small_work': [False],
        'personal': [False]
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
    cfg = load_config()
    data = load_day_total(364)
    milestones = fix_milestones()
    personal_done = data.loc[0, "Personal"]
    work_done = data.loc[0, "Work"]
    work_goal = cfg["WORK_DAILY_GOAL"]

    # Check personal
    if not milestones.loc[0, "personal"]:
        if personal_done >= max(
            cfg["PERSONAL_DAILY_GOAL"],
            work_done * cfg["WORK_TO_PERSONAL_MULTIPLIER"]
        ):
            message = "Passed your personal daily limit. "
            message += "Consider studying more!"
            milestones.loc[0, "personal"] = True
            send_notification("❌ Misstep detected! ❌", message, "bad")

    # Check work
    if not milestones.loc[0, "small_work"]:
        if work_done >= cfg["SMALL_WORK_DAILY_GOAL"]:
            message = "Completed the small daily study goal. "
            message += "Congratulations for your consistency!"
            milestones.loc[0, "small_work"] = True
            send_notification("💡 Progress made! 💡", message, "neutral")

    if not milestones.loc[0, "work_25"]:
        if work_done >= work_goal * 0.25:
            message = "Completed 25% of the daily study goal. "
            message += f"Consider studying {int(work_goal * 60 * 0.75)}m "
            message += "to stay on track!"
            milestones.loc[0, "work_25"] = True
            send_notification("💡 Progress made! 💡", message, "neutral")

    if not milestones.loc[0, "work_50"]:
        if work_done >= work_goal * 0.50:
            message = "Completed 50% of the daily study goal. "
            message += f"Consider studying {int(work_goal * 60 * 0.50)}m "
            message += "to stay on track!"
            milestones.loc[0, "work_50"] = True
            send_notification("💡 Progress made! 💡", message, "neutral")

    if not milestones.loc[0, "work_75"]:
        if work_done >= work_goal * 0.75:
            message = "Completed 75% of the daily study goal. "
            message += f"Consider studying {int(work_goal * 60 * 0.25)}m "
            message += "to stay on track!"
            milestones.loc[0, "work_75"] = True
            send_notification("💡 Progress made! 💡", message, "neutral")

    if not milestones.loc[0, "work_100"]:
        if work_done >= work_goal:
            message = "Completed 100% of the daily study goal. "
            message += "Congratulations! +1 streak point"
            milestones.loc[0, "work_100"] = True
            send_notification("🎉 Milestone achieved! 🎉", message, "good")

    # Update milestones dataframe
    save_dataframe(milestones, "milestones")


def study_advisor():
    """
    Main study advisor functions that coordinates all functionality.
    """
    while True:
        cfg = load_config()
        check_milestones()

        time.sleep(cfg["STUDY_ADVISOR_INTERVAL"])
