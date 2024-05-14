from datetime import datetime, timedelta
from airflow.decorators import task, dag
from os.path import join
import os
import shutil
import sys

sys.path.append('/autotracker/src')
from helper_io import load_config


BACKUP_FOLDER = '/autotracker/backup'
DATABASE_FOLDER = '/autotracker/data/activity.db'
DATE_FORMAT = "%Y-%m-%d-%H-%M"
default_args = {
    "owner": "autotracker",
    "retries": 2,
    "retry_delay": timedelta(seconds=10),
    "start_date": datetime(2024, 1, 1)
}


@dag(default_args=default_args, schedule=timedelta(minutes=15), catchup=False)
def backup():
    @task
    def create_folder() -> None:
        os.makedirs('autotracker/backup', exist_ok=True)

    @task
    def create_backup() -> None:
        cfg = load_config()
        files = os.listdir(BACKUP_FOLDER)
        files.sort()
        if files:
            # Check if backup is needed
            now = datetime.now()
            last_backup = now - datetime.strptime(files[-1][:-3], DATE_FORMAT)
            if last_backup < timedelta(minutes=cfg["BACKUP_INTERVAL"]):
                return

        # Create backup
        now = datetime.now()
        shutil.copy2(
            DATABASE_FOLDER,
            join(BACKUP_FOLDER, f'{now.strftime(DATE_FORMAT)}.db')
        )

    @task
    def delete_old_files() -> None:
        cfg = load_config()
        backup_count = cfg["NUMBER_OF_BACKUPS"]
        files = os.listdir(BACKUP_FOLDER)
        files.sort()
        num_files = len(files)

        if num_files <= backup_count:
            return

        for file in files[:num_files-backup_count]:
            os.remove(join(BACKUP_FOLDER, file))

    create_folder() >> create_backup() >> delete_old_files()


backup()
