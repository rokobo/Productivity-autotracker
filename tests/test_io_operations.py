"""Test input and output functions."""
# pylint: disable=import-error
import os
import pandas as pd
from helper_io import save_dataframe, load_dataframe, load_input_time,\
    load_config, load_lastest_row, \
    modify_latest_row, append_to_database, load_activity_between, \
    load_categories

CFG = load_config()


def test_data_integrity() -> None:
    """Tests if data remains the same after saving and loading."""
    dataframe = pd.DataFrame({'col1': ["1"]})
    save_dataframe(dataframe, '__test1__')
    loaded_dataframe = load_dataframe('__test1__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'col1': [1], 'col2': ["2"]})
    save_dataframe(dataframe, '__test1__')
    loaded_dataframe = load_dataframe('__test1__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({
        'start_time': [111], 'end_time': [222],
        'app': ["test_app"], 'info': ["test_info"],
        'handle': 333, 'pid': 444, 'process_name': "test.exe",
        'url': "test.com/test", 'domain': "test.com"
    })
    save_dataframe(dataframe, '__test1__')
    loaded_dataframe = load_dataframe('__test1__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    # Clean files
    path = os.path.join(CFG["WORKSPACE"], 'data/__test1__.db')
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
    path = os.path.join(CFG["WORKSPACE"], 'data/__test2__.db')
    os.remove(path)


def test_load_latest_row() -> None:
    """Tests load_latest_row function."""
    dataframe = pd.DataFrame({'col1': ["1"]})
    save_dataframe(dataframe, '__test3__')
    loaded_dataframe = load_lastest_row('__test3__')
    assert dataframe.tail(1).equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'col1': [1], 'col2': ["2"]})
    save_dataframe(dataframe, '__test3__')
    loaded_dataframe = load_lastest_row('__test3__')
    assert dataframe.tail(1).equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'col2': [5], 'col3': [3], 'col1': [7]})
    save_dataframe(dataframe, '__test3__')
    loaded_dataframe = load_dataframe('__test3__')
    assert dataframe.tail(1).equals(loaded_dataframe.drop('rowid', axis=1))

    # Clean files
    path = os.path.join(CFG["WORKSPACE"], 'data/__test3__.db')
    os.remove(path)


def test_modify_latest_row() -> None:
    """Tests the modify_latest_row function."""
    dataframe = pd.DataFrame({'col1': ["1"]})
    save_dataframe(dataframe, '__test4__')
    new_dataframe = load_lastest_row('__test4__')
    new_dataframe.loc[0, 'col1'] = "2"
    modify_latest_row('__test4__', new_dataframe, ['col1'])
    loaded_dataframe = load_lastest_row('__test4__')
    assert new_dataframe.equals(loaded_dataframe)

    dataframe = pd.DataFrame({'col1': [1], 'col2': ["2"]})
    save_dataframe(dataframe, '__test4__')
    new_dataframe = load_lastest_row('__test4__')
    new_dataframe.loc[0, 'col1'] = 5
    modify_latest_row('__test4__', new_dataframe, ['col1'])
    loaded_dataframe = load_lastest_row('__test4__')
    assert new_dataframe.equals(loaded_dataframe)

    dataframe = pd.DataFrame({'col1': [1], 'col2': [2], 'col3': [3]})
    save_dataframe(dataframe, '__test4__')
    new_dataframe = load_lastest_row('__test4__')
    new_dataframe.loc[0, 'col1'] = 4
    new_dataframe.loc[0, 'col3'] = 6
    modify_latest_row('__test4__', new_dataframe, ['col1', 'col3'])
    loaded_dataframe = load_lastest_row('__test4__')
    assert new_dataframe.equals(loaded_dataframe)

    new_dataframe = load_lastest_row('__test4__')
    modify_latest_row('__test4__', new_dataframe, ['col1', 'col3'])
    loaded_dataframe = load_lastest_row('__test4__')
    assert new_dataframe.equals(loaded_dataframe)

    # Clean files
    path = os.path.join(CFG["WORKSPACE"], 'data/__test4__.db')
    os.remove(path)


def test_append_to_database() -> None:
    """Tests the append_to_database function."""
    dataframe = pd.DataFrame({'col1': ["1"]})
    save_dataframe(dataframe, '__test5__')
    new_row = pd.DataFrame({'col1': ["3"]})
    append_to_database('__test5__', new_row)
    joined_dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    loaded_dataframe = load_dataframe('__test5__')
    assert joined_dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    # Clean files
    path = os.path.join(CFG["WORKSPACE"], 'data/__test5__.db')
    os.remove(path)


def test_load_activity_between() -> None:
    """Tests the load_activity_between function."""
    dataframe = pd.DataFrame({'start_time': [2], 'end_time': [3]})
    save_dataframe(dataframe, '__test6__')
    loaded_dataframe = load_activity_between(1, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))
    loaded_dataframe = load_activity_between(2, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))
    loaded_dataframe = load_activity_between(1, 3, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))
    loaded_dataframe = load_activity_between(2, 3, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'start_time': [2, 4, 3], 'end_time': [3, 5, 4]})
    save_dataframe(dataframe, '__test6__')
    loaded_dataframe = load_activity_between(1, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'start_time': [4, 3], 'end_time': [5, 4]})
    loaded_dataframe = load_activity_between(3, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'start_time': [2, 3], 'end_time': [3, 4]})
    loaded_dataframe = load_activity_between(2, 4, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    dataframe = pd.DataFrame({'start_time': [4], 'end_time': [5]})
    loaded_dataframe = load_activity_between(4, 9, '__test6__')
    assert dataframe.equals(loaded_dataframe.drop('rowid', axis=1))

    # Clean files
    path = os.path.join(CFG["WORKSPACE"], 'data/__test6__.db')
    os.remove(path)


def test_load_config() -> None:
    """Tests the load_config function."""
    config = load_config()
    assert config
    assert isinstance(config, dict)
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert config["WORKSPACE"] == workspace


def test_load_categories() -> None:
    """Tests the load_categories function."""
    categories = load_categories()
    assert categories
    assert isinstance(categories, dict)
    assert "WORK_APPS" in categories
    assert "PERSONAL_APPS" in categories
    assert "WORK_DOMAINS" in categories
    assert "PERSONAL_DOMAINS" in categories
    assert "WORK_KEYWORDS" in categories
    assert "PERSONAL_KEYWORDS" in categories
