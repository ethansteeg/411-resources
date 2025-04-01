import pytest
from contextlib import contextmanager
import sqlite3
import re

from boxing.models.boxers_model import (
    create_boxer,
    Boxer,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    delete_boxer,
    update_boxer_stats
)

# ----------------------------
# Fixtures
# ----------------------------

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r"\s+", " ", sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor

# ----------------------------
# Create Boxer
# ----------------------------

def test_create_boxer_valid(mock_cursor):
    create_boxer("Boxer A", 160, 70, 72.0, 25)
    insert_sql = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    assert normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0]) == insert_sql
    assert mock_cursor.execute.call_args_list[1][0][1] == ("Boxer A", 160, 70, 72.0, 25)

def test_create_boxer_duplicate(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    with pytest.raises(ValueError, match="Boxer With name 'Boxer A' already exists"):
        create_boxer("Boxer A", 160, 70, 72.0, 25)

def test_create_boxer_invalid_inputs():
    with pytest.raises(ValueError, match="Invalid weight: 120"):
        create_boxer("Boxer B", 120, 70, 72.0, 25)
    with pytest.raises(ValueError, match="Invalid height: 0"):
        create_boxer("Boxer B", 150, 0, 72.0, 25)
    with pytest.raises(ValueError, match="Invalid reach: 0.0"):
        create_boxer("Boxer B", 150, 70, 0.0, 25)
    with pytest.raises(ValueError, match="Invalid age: 17"):
        create_boxer("Boxer B", 150, 70, 72.0, 17)

def test_create_boxer_sql_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("DB error")
    with pytest.raises(sqlite3.Error, match="DB error"):
        create_boxer("Boxer C", 150, 70, 72.0, 25)

# ----------------------------
# Delete Boxer
# ----------------------------

def test_delete_boxer_valid(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    delete_boxer(None, 1)
    assert normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0]) == "DELETE FROM boxers WHERE id = ?"
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)

def test_delete_boxer_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(None, 999)

def test_delete_boxer_invalid_id():
    with pytest.raises(ValueError, match="Invalid Boxer ID: -1"):
        delete_boxer(None, -1)

def test_delete_boxer_db_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("DB fail")
    with pytest.raises(sqlite3.Error, match="DB fail"):
        delete_boxer(None, 1)

# ----------------------------
# Get Boxer by ID and Name
# ----------------------------

def test_get_boxer_by_id_valid(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Boxer A", 150, 70, 72.0, 25)
    boxer = get_boxer_by_id(1)
    assert boxer.name == "Boxer A"
    assert boxer.weight_class == "LIGHTWEIGHT"

def test_get_boxer_by_id_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)

def test_get_boxer_by_id_invalid():
    with pytest.raises(ValueError, match="Invalid boxer ID: -1"):
        get_boxer_by_id(-1)

def test_get_boxer_by_id_db_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("DB fail")
    with pytest.raises(sqlite3.Error):
        get_boxer_by_id(1)

def test_get_boxer_by_name_valid(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Boxer A", 160, 70, 72.0, 25)
    boxer = get_boxer_by_name("Boxer A")
    assert boxer.name == "Boxer A"

def test_get_boxer_by_name_invalid():
    with pytest.raises(ValueError, match="Invalid boxer name: "):
        get_boxer_by_name("")

def test_get_boxer_by_name_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer 'Ghost' not found"):
        get_boxer_by_name("Ghost")

def test_get_boxer_by_name_db_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("DB issue")
    with pytest.raises(sqlite3.Error):
        get_boxer_by_name("Boxer A")

# ----------------------------
# Weight Class
# ----------------------------

def test_get_weight_class_valid():
    assert get_weight_class(125) == "FEATHERWEIGHT"
    assert get_weight_class(150) == "LIGHTWEIGHT"
    assert get_weight_class(180) == "MIDDLEWEIGHT"
    assert get_weight_class(205) == "HEAVYWEIGHT"

def test_get_weight_class_invalid():
    with pytest.raises(ValueError, match="Invalid weight: 124"):
        get_weight_class(124)

# ----------------------------
# Update Boxer Stats
# ----------------------------

def test_update_boxer_stats_valid_win(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    update_boxer_stats(1, "win")
    assert "UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?" in mock_cursor.execute.call_args_list[1][0][0]

def test_update_boxer_stats_valid_loss(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    update_boxer_stats(1, "loss")
    assert "UPDATE boxers SET fights = fights + 1 WHERE id = ?" in mock_cursor.execute.call_args_list[1][0][0]

def test_update_boxer_stats_invalid_result():
    with pytest.raises(ValueError, match="Invalid result: draw"):
        update_boxer_stats(1, "draw")

def test_update_boxer_stats_invalid_id():
    with pytest.raises(ValueError, match="Invalid boxer ID: -1"):
        update_boxer_stats(-1, "win")

def test_update_boxer_stats_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 1 not found"):
        update_boxer_stats(1, "win")

def test_update_boxer_stats_db_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("DB error")
    with pytest.raises(sqlite3.Error):
        update_boxer_stats(1, "win")