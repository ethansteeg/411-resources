# tests/test_boxers_model.py

import sqlite3
from unittest.mock import patch, Mock
import pytest

from boxing.models import Boxer, get_weight_class


def test_boxer_creation():
    """Test the creation of a Boxer object."""
    boxer = Boxer(
        id=1,
        name="Mike Tyson",
        weight=220,
        height=70,
        reach=71.0,
        age=54,
    )
    assert boxer.id == 1
    assert boxer.name == "Mike Tyson"
    assert boxer.weight == 220
    assert boxer.height == 70
    assert boxer.reach == 71.0
    assert boxer.age == 54
    assert boxer.weight_class == "HEAVYWEIGHT"  # Test auto weight class


def test_get_weight_class():
    """Test the get_weight_class function."""
    assert get_weight_class(220) == "HEAVYWEIGHT"
    assert get_weight_class(180) == "MIDDLEWEIGHT"
    assert get_weight_class(150) == "LIGHTWEIGHT"
    assert get_weight_class(125) == "FEATHERWEIGHT"


def test_get_weight_class_invalid_weight():
    """Test get_weight_class with invalid weight input."""
    with pytest.raises(ValueError, match="Invalid weight: 100. Weight must be at least 125."):
        get_weight_class(100)


def test_create_boxer_valid_input(mocker):
    """Test create_boxer with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Boxer doesn't exist

    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        Boxer.create_boxer("Test Boxer", 160, 70, 72.0, 25)

    mock_cursor.execute.assert_called_with(
        """INSERT INTO boxers (name, weight, height, reach, age) VALUES (?, ?, ?, ?, ?)""",
        ("Test Boxer", 160, 70, 72.0, 25),
    )
    mock_conn.commit.assert_called_once()


def test_create_boxer_invalid_weight(mocker):
    """Test create_boxer with invalid weight input."""
    with pytest.raises(ValueError, match="Invalid weight: 100. Must be at least 125."):
        Boxer.create_boxer("Test Boxer", 100, 70, 72.0, 25)


def test_create_boxer_duplicate_name(mocker):
    """Test create_boxer with duplicate boxer name."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)  # Boxer exists

    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer With name 'Test Boxer' already exists"):
            Boxer.create_boxer("Test Boxer", 160, 70, 72.0, 25)


def test_create_boxer_database_error(mocker):
    """Test create_boxer with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = sqlite3.Error("Database error")

    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        with pytest.raises(sqlite3.Error, match="Database error"):
            Boxer.create_boxer("Test Boxer", 160, 70, 72.0, 25)


def test_delete_boxer_valid_input(mocker):
    """Test delete_boxer with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)  # Boxer exists
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        boxer_instance = Boxer(1, "test", 1, 1, 1.0, 1)  # dummy instance
        boxer_instance.delete_boxer(1)

    mock_cursor.execute.assert_called_with("DELETE FROM boxers WHERE id = ?", (1,))
    mock_conn.commit.assert_called_once()


def test_delete_boxer_invalid_id(mocker):
    """Test delete_boxer with invalid boxer ID."""
    boxer_instance = Boxer(1, "test", 1, 1, 1.0, 1)  # dummy instance
    with pytest.raises(ValueError, match="Invalid Boxer ID: -1. Must be a non-negative integer."):
        boxer_instance.delete_boxer(-1)


def test_delete_boxer_not_found(mocker):
    """Test delete_boxer with boxer not found."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Boxer doesn't exist
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        boxer_instance = Boxer(1, "test", 1, 1, 1.0, 1)  # dummy instance
        with pytest.raises(ValueError, match="Boxer with ID 1 not found."):
            boxer_instance.delete_boxer(1)


def test_delete_boxer_database_error(mocker):
    """Test delete_boxer with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = sqlite3.Error("Database error")
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        boxer_instance = Boxer(1, "test", 1, 1, 1.0, 1)  # dummy instance
        with pytest.raises(sqlite3.Error, match="Database error"):
            boxer_instance.delete_boxer(1)


def test_get_leaderboard_valid_input(mocker):
    """Test get_leaderboard with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, "Test Boxer", 160, 70, 72.0, 25, 10, 8, 0.8)]
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        leaderboard = Boxer(1, "test", 1, 1, 1.0, 1).get_leaderboard()
        assert len(leaderboard) == 1
        assert leaderboard[0]["name"] == "Test Boxer"
        assert leaderboard[0]["win_pct"] == 80.0


def test_get_leaderboard_invalid_sort_by(mocker):
    """Test get_leaderboard with invalid sort_by parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by paramater: invalid"):
        Boxer(1, "test", 1, 1, 1.0, 1).get_leaderboard(sort_by="invalid")


def test_get_leaderboard_database_error(mocker):
    """Test get_leaderboard with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = sqlite3.Error("Database error")
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        with pytest.raises(sqlite3.Error, match="Database error: Database error"):
            Boxer(1, "test", 1, 1, 1.0, 1).get_leaderboard()


def test_get_boxer_by_id_valid_input(mocker):
    """Test get_boxer_by_id with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, "Test Boxer", 160, 70, 72.0, 25)
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        boxer = Boxer.get_boxer_by_id(1)
        assert boxer.name == "Test Boxer"


def test_get_boxer_by_id_invalid_id(mocker):
    """Test get_boxer_by_id with invalid boxer ID."""
    with pytest.raises(ValueError, match="Invalid boxer ID: -1. Must be a non-negative integer."):
        Boxer.get_boxer_by_id(-1)


def test_get_boxer_by_id_not_found(mocker):
    """Test get_boxer_by_id with boxer not found."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with ID 1 not found."):
            Boxer.get_boxer_by_id(1)


def test_get_boxer_by_id_database_error(mocker):
    """Test get_boxer_by_id with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = sqlite3.Error("Database error")
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        with pytest.raises(sqlite3.Error, match="Database error: Database error"):
            Boxer.get_boxer_by_id(1)


def test_get_boxer_by_name_valid_input(mocker):
    """Test get_boxer_by_name with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, "Test Boxer", 160, 70, 72.0, 25)
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        boxer = Boxer.get_boxer_by_name("Test Boxer")
        assert boxer.id == 1


def test_get_boxer_by_name_invalid_name(mocker):
    """Test get_boxer_by_name with invalid boxer name."""
    with pytest.raises(ValueError, match="Invalid boxer name: None. Must be a non-empty string."):
        Boxer.get_boxer_by_name(None)


def test_get_boxer_by_name_not_found(mocker):
    """Test get_boxer_by_name with boxer not found."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer 'Test Boxer' not found."):
            Boxer.get_boxer_by_name("Test Boxer")


def test_get_boxer_by_name_database_error(mocker):
    """Test get_boxer_by_name with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = sqlite3.Error("Database error")
    with patch("boxing.models.get_db_connection", return_value=mock_conn):
        with pytest.raises(sqlite3.Error, match="Database error: Database error"):
            Boxer.get_boxer_by_name("Test Boxer")


def test_update_boxer_stats_valid_input(mocker):
    """Test update_boxer_stats with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)