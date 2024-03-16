"""Tests modules for pylint problems."""
import os
from pylint.lint import Run

workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_folder = os.path.join(workspace, "src")
pages_folder = os.path.join(workspace, "src/pages")


def test_pylint_functions_activity() -> None:
    """Ensures functions_activity passes pylint specifications."""
    file = os.path.join(src_folder, "functions_activity.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_functions_threads() -> None:
    """Ensures functions_threads passes pylint specifications."""
    file = os.path.join(src_folder, "functions_threads.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_helper_io() -> None:
    """Ensures helper_io passes pylint specifications."""
    file = os.path.join(src_folder, "helper_io.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_helper_server() -> None:
    """Ensures helper_server passes pylint specifications."""
    file = os.path.join(src_folder, "helper_server.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_main() -> None:
    """Ensures main passes pylint specifications."""
    file = os.path.join(src_folder, "main.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_activity() -> None:
    """Ensures layout_activity passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_activity.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_categories() -> None:
    """Ensures layout_categories passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_categories.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_configuration() -> None:
    """Ensures layout_configuration passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_configuration.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_configuration2() -> None:
    """Ensures layout_configuration2 passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_configuration2.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_credits() -> None:
    """Ensures layout_credits passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_credits.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_inputs() -> None:
    """Ensures layout_inputs passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_inputs.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_dashboard() -> None:
    """Ensures layout_dashboard passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_dashboard.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_trends() -> None:
    """Ensures layout_trends passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_trends.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_all() -> None:
    """Ensures layout_all passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_all.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_layout_menu() -> None:
    """Ensures layout_menu passes pylint specifications."""
    file = os.path.join(pages_folder, "layout_menu.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_study_advisor() -> None:
    """Ensures study_advisor passes pylint specifications."""
    file = os.path.join(src_folder, "study_advisor.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg


def test_pylint_retry_decorator() -> None:
    """Ensures retry_decorator passes pylint specifications."""
    file = os.path.join(src_folder, "retry_decorator.py")
    result = Run([file], exit=False).linter.stats
    assert result.global_note == 10, result.by_msg
