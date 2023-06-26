"""Tests modules for flake8 problems."""
import os
from flake8.api import legacy as flake8

workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_folder = os.path.join(workspace, "src")
pages_folder = os.path.join(workspace, "src/pages")


def test_flake8_functions_activity() -> None:
    """Ensures functions_activity passes flake8 specifications."""
    file = os.path.join(src_folder, "functions_activity.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_functions_threads() -> None:
    """Ensures functions_threads passes flake8 specifications."""
    file = os.path.join(src_folder, "functions_threads.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_helper_io() -> None:
    """Ensures helper_io passes flake8 specifications."""
    file = os.path.join(src_folder, "helper_io.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_helper_retry() -> None:
    """Ensures helper_retry passes flake8 specifications."""
    file = os.path.join(src_folder, "helper_retry.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_helper_server() -> None:
    """Ensures helper_server passes flake8 specifications."""
    file = os.path.join(src_folder, "helper_server.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_main() -> None:
    """Ensures main passes flake8 specifications."""
    file = os.path.join(src_folder, "main.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_activity() -> None:
    """Ensures layout_activity passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_activity.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_categories() -> None:
    """Ensures layout_categories passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_categories.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_configuration() -> None:
    """Ensures layout_configuration passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_configuration.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_configuration2() -> None:
    """Ensures layout_configuration2 passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_configuration2.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_credits() -> None:
    """Ensures layout_credits passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_credits.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_inputs() -> None:
    """Ensures layout_inputs passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_inputs.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_dashboard() -> None:
    """Ensures layout_dashboard passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_dashboard.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_goals() -> None:
    """Ensures layout_goals passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_goals.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))


def test_flake8_layout_menu() -> None:
    """Ensures layout_menu passes flake8 specifications."""
    file = os.path.join(pages_folder, "layout_menu.py")
    result = flake8.get_style_guide().check_files([file])
    assert result.total_errors == 0, result.get_statistics(('F', 'E', 'W'))
