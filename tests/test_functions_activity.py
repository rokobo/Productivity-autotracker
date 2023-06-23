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
    result = total_by_category(dataframe)
    correct = pd.DataFrame({
        'category': ['Work', 'Personal', 'Neutral'],
        'total': [0, 0.5, 0]
    })
    assert result.equals(correct), (result, correct)
