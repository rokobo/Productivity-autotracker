"""Tests modules for pylint problems."""
import os
from pylint.lint import Run

workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_folder = os.path.join(workspace, "src")
pages_folder = os.path.join(workspace, "src/pages")


def test_pylint_functions_activity() -> None:
    """Ensures functions_activity passes pylint specifications."""
    file = os.path.join(src_folder, "functions_activity.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_functions_threads() -> None:
    """Ensures functions_threads passes pylint specifications."""
    file = os.path.join(src_folder, "functions_threads.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_helper_io() -> None:
    """Ensures helper_io passes pylint specifications."""
    file = os.path.join(src_folder, "helper_io.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_helper_retry() -> None:
    """Ensures helper_retry passes pylint specifications."""
    file = os.path.join(src_folder, "helper_retry.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_helper_server() -> None:
    """Ensures helper_server passes pylint specifications."""
    file = os.path.join(src_folder, "helper_server.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_main() -> None:
    """Ensures main passes pylint specifications."""
    file = os.path.join(src_folder, "main.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_activity() -> None:
    """Ensures layout_activity passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_activity.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_categories() -> None:
    """Ensures layout_categories passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_categories.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_inputs() -> None:
    """Ensures layout_inputs passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_inputs.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_main() -> None:
    """Ensures layout_main passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_main.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_menu() -> None:
    """Ensures layout_menu passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_menu.py")
    result = Run([file], do_exit=False).linter.stats
    assert result.global_note == 10, result.by_msg
