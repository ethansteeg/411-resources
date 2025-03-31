import pytest
from unittest.mock import patch, Mock

from ..boxing.models.boxers_model import Boxer, get_boxer_by_id, get_boxer_by_name, get_leaderboard, get_weight_class


@pytest.fixture
def sample_boxer1():
    return Boxer("Boxer 1", 160, 70, 72.0, 25)

@pytest.fixture
def sample_boxer2():
    return Boxer("Boxer 2", 180, 72, 74.0, 28)

@pytest.fixture
def sample_boxer3():
    return Boxer("Boxer 3", 140, 68, 70.0, 22)

@pytest.fixture
def sample_boxers(sample_boxer1, sample_boxer2, sample_boxer3):
    return [sample_boxer1, sample_boxer2, sample_boxer3]


##################################################
# Boxer Creation and Deletion Test Cases
##################################################


def test_create_boxer_valid_input(mocker):
    """Test create_boxer with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Boxer doesn't exist

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        Boxer.create_boxer("Test Boxer", 160, 70, 72.0, 25)

    mock_cursor.execute.assert_called_with(
        """INSERT INTO boxers (name, weight, height, reach, age) VALUES (?, ?, ?, ?, ?)""",
        ("Test Boxer", 160, 70, 72.0, 25),
    )
    mock_conn.commit.assert_called_once()


def test_create_boxer_duplicate_name(mocker):
    """Test create_boxer with duplicate name."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)  # Boxer exists

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with name 'Test Boxer' already exists."):
            Boxer.create_boxer("Test Boxer", 160, 70, 72.0, 25)


def test_create_boxer_database_error(mocker):
    """Test create_boxer with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(Exception, match="Database error"):
            Boxer.create_boxer("Test Boxer", 160, 70, 72.0, 25)


def test_delete_boxer_valid_input(mocker, sample_boxer1):
    """Test delete_boxer with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 1

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        Boxer.delete_boxer(sample_boxer1.name)

    mock_cursor.execute.assert_called_with("DELETE FROM boxers WHERE name = ?", (sample_boxer1.name,))
    mock_conn.commit.assert_called_once()


def test_delete_boxer_invalid_id(mocker):
    """Test delete_boxer with invalid name."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 0

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with name 'Nonexistent Boxer' not found."):
            Boxer.delete_boxer("Nonexistent Boxer")


def test_delete_boxer_database_error(mocker, sample_boxer1):
    """Test delete_boxer with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(Exception, match="Database error"):
            Boxer.delete_boxer(sample_boxer1.name)


##################################################
# Boxer Retrieval Test Cases
##################################################


def test_get_boxer_by_id_valid_input(mocker, sample_boxer1):
    """Test get_boxer_by_id with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, sample_boxer1.name, sample_boxer1.weight, sample_boxer1.height, sample_boxer1.reach, sample_boxer1.age)

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        boxer = get_boxer_by_id(1)

    assert boxer == (1, sample_boxer1.name, sample_boxer1.weight, sample_boxer1.height, sample_boxer1.reach, sample_boxer1.age)


def test_get_boxer_by_id_invalid_id(mocker):
    """Test get_boxer_by_id with invalid id."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with id 2 not found."):
            get_boxer_by_id(2)


def test_get_boxer_by_id_database_error(mocker):
    """Test get_boxer_by_id with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(Exception, match="Database error"):
            get_boxer_by_id(1)


def test_get_boxer_by_name_valid_input(mocker, sample_boxer1):
    """Test get_boxer_by_name with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, sample_boxer1.name, sample_boxer1.weight, sample_boxer1.height, sample_boxer1.reach, sample_boxer1.age)

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        boxer = get_boxer_by_name(sample_boxer1.name)

    assert boxer == (1, sample_boxer1.name, sample_boxer1.weight, sample_boxer1.height, sample_boxer1.reach, sample_boxer1.age)


def test_get_boxer_by_name_invalid_name(mocker):
    """Test get_boxer_by_name with invalid name."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with name 'Nonexistent Boxer' not found."):
            get_boxer_by_name("Nonexistent Boxer")


def test_get_boxer_by_name_database_error(mocker):
    """Test get_boxer_by_name with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(Exception, match="Database error"):
            get_boxer_by_name("Any Name")


##################################################
# Leaderboard Test Cases
##################################################

def test_get_leaderboard_valid_input(mocker, sample_boxers):
    """Test get_leaderboard with valid input."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(b.name, b.weight, b.height, b.reach, b.age) for b in sample_boxers]

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        leaderboard = get_leaderboard(mock_conn, "weight")

    assert leaderboard == [(b.name, b.weight, b.height, b.reach, b.age) for b in sample_boxers]


def test_get_leaderboard_invalid_sort_by(mocker):
    """Test get_leaderboard with invalid sort_by parameter."""
    mock_conn = mocker.MagicMock()

    with pytest.raises(ValueError, match=r"Invalid sort by parameter."):
        get_leaderboard(mock_conn, "invalid_sort")


def test_get_leaderboard_database_error(mocker):
    """Test get_leaderboard with database error."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    with patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn):
        with pytest.raises(Exception, match="Database error"):
            get_leaderboard(mock_conn, "weight")

##################################################
# Weight Class Test Cases
##################################################

def test_get_weight_class_valid_input():
    assert get_weight_class(130) == "Lightweight"
    assert get_weight_class(150) == "Welterweight"
    assert get_weight_class(170) == "Middleweight"
    assert get_weight_class(200) == "Light Heavyweight"
    assert get_weight_class(220) == "Heavyweight"

def test_get_weight_class_invalid_input():
  with pytest.raises(ValueError, match = "Invalid weight: 1. Weight must be at least 125."):
    get_weight_class(1)