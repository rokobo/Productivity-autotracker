"""Test activity functions."""
# pylint: disable=import-error
import pandas as pd
from helper_io import load_config
from functions_activity import total_by_category

CFG = load_config()


def test_total_by_category() -> None:
    """Tests the total_by_category function."""
    dataframe = pd.DataFrame({
        'process_name': ['test.exe'],
        'subtitle': ['info'],
        'category': ['Personal'],
        'method': ['(A)'],
        'duration': ['30 minutes'],
        'total': [0.5],
        'rowid': [1]
    })
    categories = ['Work', 'Personal', 'Neutral']
    result = total_by_category(dataframe)
    correct = pd.DataFrame({
        'category': categories, 'total': [0, 0.5, 0]})
    assert result.equals(correct), (result, correct)

    dataframe.loc[0, 'category'] = "Neutral"
    dataframe.loc[0, 'total'] = 0.75
    result = total_by_category(dataframe)
    correct = pd.DataFrame({
        'category': categories, 'total': [0, 0, 0.75]})
    assert result.equals(correct), dataframe

    dataframe.loc[0, 'category'] = "Personal"
    dataframe.loc[0, 'total'] = 1.2
    result = total_by_category(dataframe)
    correct = pd.DataFrame({
        'category': categories, 'total': [0, 1.2, 0]})
    assert result.equals(correct), dataframe

    dataframe = pd.DataFrame({
        'process_name': ['test.exe', 'test2.exe'],
        'subtitle': ['info', 'info2'],
        'category': ['Personal', 'Personal'],
        'method': ['(A)', '(D)'],
        'duration': ['30 minutes', '1 hour'],
        'total': [0.5, 1],
        'rowid': [1, 2]
    })
    categories = ['Work', 'Personal', 'Neutral']
    result = total_by_category(dataframe)
    correct = pd.DataFrame({
        'category': categories, 'total': [0, 1.5, 0]})
    assert result.equals(correct), (result, correct)

    dataframe.loc[0, 'category'] = "Neutral"
    dataframe.loc[0, 'total'] = 0.75
    result = total_by_category(dataframe)
    correct = pd.DataFrame({
        'category': categories, 'total': [0, 1, 0.75]})
    assert result.equals(correct), dataframe
