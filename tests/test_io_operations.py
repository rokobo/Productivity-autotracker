"""Test input and output functions."""
# pylint: disable=import-error
import os
import time
import shutil
import pandas as pd
from helper_io import save_dataframe, load_dataframe, load_input_time,\
    clean_and_select_newest_url, load_urls, load_config, load_lastest_row, \
    modify_latest_row, append_to_database, load_activity_between

cfg = load_config()


def test_data_integrity() -> None:
    """Tests if data remains the same after saving and loading."""
    dataframe = pd.DataFrame({'col1': ["1"]})
    save_dataframe(dataframe, '__test1__')
    _, loaded_dataframe = load_dataframe('__test1__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'col1': [1], 'col2': ["2"]})
    save_dataframe(dataframe, '__test1__')
    _, loaded_dataframe = load_dataframe('__test1__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({
        'start_time': [111], 'end_time': [222],
        'app': ["test_app"], 'info': ["test_info"],
        'handle': 333, 'pid': 444, 'process_name': "test.exe",
        'url': "test.com/test", 'domain': "test.com"
    })
    save_dataframe(dataframe, '__test1__')
    _, loaded_dataframe = load_dataframe('__test1__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    # Clean files
    path = os.path.join(cfg["WORKSPACE"], f'data/__test1__.db')
    os.remove(path)


def test_load_input_time() -> None:
    """Tests load_input_time function."""
    dataframe = pd.DataFrame({'col1': [45]})
    save_dataframe(dataframe, '__test2__')
    input_time = load_input_time('__test2__')
    assert input_time == 45

    dataframe = pd.DataFrame({'col1': [12], 'col2': [45]})
    save_dataframe(dataframe, '__test2__')
    input_time = load_input_time('__test2__')
    assert input_time == 12

    dataframe = pd.DataFrame({'col1': [84], 'col2': [56], 'col3': [75]})
    save_dataframe(dataframe, '__test2__')
    input_time = load_input_time('__test2__')
    assert input_time == 84

    # Clean files
    path = os.path.join(cfg["WORKSPACE"], f'data/__test2__.db')
    os.remove(path)


def test_load_latest_row() -> None:
    """Tests load_latest_row function."""
    dataframe = pd.DataFrame({'col1': ["1"]})
    save_dataframe(dataframe, '__test3__')
    _, loaded_dataframe = load_lastest_row('__test3__')
    assert dataframe.tail(1).equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'col1': [1], 'col2': ["2"]})
    save_dataframe(dataframe, '__test3__')
    _, loaded_dataframe = load_lastest_row('__test3__')
    assert dataframe.tail(1).equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'col2': [5], 'col3': [3], 'col1': [7]})
    save_dataframe(dataframe, '__test3__')
    _, loaded_dataframe = load_dataframe('__test3__')
    assert dataframe.tail(1).equals(loaded_dataframe.drop('rowid', axis=1))

    # Clean files
    path = os.path.join(cfg["WORKSPACE"], f'data/__test3__.db')
    os.remove(path)


def test_modify_latest_row() -> None:
    """Tests the modify_latest_row function."""
    dataframe = pd.DataFrame({'col1': ["1"]})
    save_dataframe(dataframe, '__test4__')
    _, new_dataframe = load_lastest_row('__test4__')
    new_dataframe.loc[0, 'col1'] = "2"
    modify_latest_row('__test4__', new_dataframe, ['col1'])
    _, loaded_dataframe = load_lastest_row('__test4__')
    assert new_dataframe.equals(loaded_dataframe)

    dataframe = pd.DataFrame({'col1': [1], 'col2': ["2"]})
    save_dataframe(dataframe, '__test4__')
    _, new_dataframe = load_lastest_row('__test4__')
    new_dataframe.loc[0, 'col1'] = 5
    modify_latest_row('__test4__', new_dataframe, ['col1'])
    _, loaded_dataframe = load_lastest_row('__test4__')
    assert new_dataframe.equals(loaded_dataframe)

    dataframe = pd.DataFrame({'col1': [1], 'col2': [2], 'col3': [3]})
    save_dataframe(dataframe, '__test4__')
    _, new_dataframe = load_lastest_row('__test4__')
    new_dataframe.loc[0, 'col1'] = 4
    new_dataframe.loc[0, 'col3'] = 6
    modify_latest_row('__test4__', new_dataframe, ['col1', 'col3'])
    _, loaded_dataframe = load_lastest_row('__test4__')
    assert new_dataframe.equals(loaded_dataframe)

    _, new_dataframe = load_lastest_row('__test4__')
    modify_latest_row('__test4__', new_dataframe, ['col1', 'col3'])
    _, loaded_dataframe = load_lastest_row('__test4__')
    assert new_dataframe.equals(loaded_dataframe)

    # Clean files
    path = os.path.join(cfg["WORKSPACE"], f'data/__test4__.db')
    os.remove(path)


def test_append_to_database() -> None:
    """Tests the append_to_database function."""
    dataframe = pd.DataFrame({'col1': ["1"]})
    save_dataframe(dataframe, '__test5__')
    new_row = pd.DataFrame({'col1': ["3"]})
    append_to_database('__test5__', new_row)
    joined_dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    _, loaded_dataframe = load_dataframe('__test5__')
    assert joined_dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    # Clean files
    path = os.path.join(cfg["WORKSPACE"], f'data/__test5__.db')
    os.remove(path)


def test_load_activity_between() -> None:
    """Tests the load_activity_between function."""
    dataframe = pd.DataFrame({'start_time': [2], 'end_time': [3]})
    save_dataframe(dataframe, '__test6__')
    _, loaded_dataframe = load_activity_between(1, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))
    _, loaded_dataframe = load_activity_between(2, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))
    _, loaded_dataframe = load_activity_between(1, 3, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))
    _, loaded_dataframe = load_activity_between(2, 3, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'start_time': [2, 4, 3], 'end_time': [3, 5, 4]})
    save_dataframe(dataframe, '__test6__')
    _, loaded_dataframe = load_activity_between(1, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'start_time': [4, 3], 'end_time': [5, 4]})
    _, loaded_dataframe = load_activity_between(3, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'start_time': [2, 3], 'end_time': [3, 4]})
    _, loaded_dataframe = load_activity_between(2, 4, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'start_time': [4], 'end_time': [5]})
    _, loaded_dataframe = load_activity_between(4, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    # Clean files
    path = os.path.join(cfg["WORKSPACE"], f'data/__test6__.db')
    os.remove(path)


def test_clean_and_selet() -> None:
    """Tests clean_and_select_newest_url function."""
    workspace = os.path.dirname(os.path.abspath(__file__))
    test_folder = os.path.join(workspace, "__test_dir1__/")
    os.makedirs(test_folder, exist_ok=True)

    file_path = os.path.join(test_folder, "file0.txt")
    open(file_path, 'w', encoding="utf-8").close()
    _, newest = clean_and_select_newest_url(test_folder)
    assert os.path.normpath(newest) == os.path.normpath(file_path)

    for i in range(1, 4):
        file_path = os.path.join(test_folder, f"file{i}.txt")
        open(file_path, 'w', encoding="utf-8").close()
        time.sleep(0.1)
    _, newest = clean_and_select_newest_url(test_folder)
    assert os.path.normpath(newest) == os.path.normpath(file_path)

    for i in range(10, 3, -1):
        file_path = os.path.join(test_folder, f"file{i}.txt")
        open(file_path, 'w', encoding="utf-8").close()
        time.sleep(0.1)
    _, newest = clean_and_select_newest_url(test_folder)
    assert os.path.normpath(newest) == os.path.normpath(file_path)

    # Clean files
    shutil.rmtree(test_folder)


def test_load_urls() -> None:
    """Tests the load_urls function."""
    workspace = os.path.dirname(os.path.abspath(__file__))
    test_folder = os.path.join(workspace, "__test_dir2__/")
    os.makedirs(test_folder, exist_ok=True)

    file_path = os.path.join(test_folder, "file67.txt")
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write("Test|-|test.gov" + '\n')
    _, urls = load_urls(test_folder)
    assert urls == [("Test", "test.gov")]

    urls_list = ["Test title|-|test.com", "test2|-|tester.org"]
    file_path = os.path.join(test_folder, "file0.txt")
    with open(file_path, 'w', encoding="utf-8") as file:
        for item in urls_list:
            file.write(item + '\n')
    _, urls = load_urls(test_folder)
    assert urls == [("Test title", "test.com"), ("test2", "tester.org")]

    for i in range(1, 5):
        file_path = os.path.join(test_folder, f"file{i}.txt")
        open(file_path, 'w', encoding="utf-8").close()
        time.sleep(0.1)
    file_path = os.path.join(test_folder, "file0.txt")
    with open(file_path, 'w', encoding="utf-8") as file:
        for item in urls_list:
            file.write(item + '\n')
    _, urls = load_urls(test_folder)
    assert urls == [("Test title", "test.com"), ("test2", "tester.org")]

    # Clean files
    shutil.rmtree(test_folder)


def test_load_config() -> None:
    """Tests the load_config function."""
    config = load_config()
    assert config
    assert isinstance(config, dict)
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert config["WORKSPACE"] == workspace
