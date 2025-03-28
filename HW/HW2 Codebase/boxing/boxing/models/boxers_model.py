from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None


    def __post_init__(self):
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class

    
    def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:

        """
        Creates a new boxer in database

        Args:
            name (str): name of boxer 
            weight (int): weight of boxer in lb 
            height (int): height of bxoer in inches 
            reach (float): reach of boxer in inches
            age (int): age of the boxer
        
        Raises: 
            ValueError: If any input parameter is invalid or if a boxer with the same name already exists 
            sqlite3.Error: If a database error occurs
        """
      
        logger.info(f"Creating Boxer: {name}")

        if weight < 125:
            logger.error(f"Invalid weight: {weight}. Must be at least 125")
            raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
        
        if height <= 0:
            logger.error(f"Invalid height: {height}. Must be greater than 0")
            raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
        
        if reach <= 0:
            logger.error(f"Invalid reach: {reach}. Must be greater than 0.")
            raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
        
        if not (18 <= age <= 40):
            logger.error(f"Invalid age: {age}. Must be between 18 and 40")
            raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Check if the boxer already exists (name must be unique)
                cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
                if cursor.fetchone():
                    logger.error(f"Boxer With name '{name}' already exists")
                    raise ValueError(f"Boxer With name '{name}' already exists")

                cursor.execute("""
                    INSERT INTO boxers (name, weight, height, reach, age)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, weight, height, reach, age))

                conn.commit()
                logger.info(f"Boxer {name} created successfully.")

        except sqlite3.IntegrityError:
            logger.error(f"Boxer With Name '{name}' already exists")
            raise ValueError(f"Boxer With Name '{name}' already exists")

        except sqlite3.Error as e:
            logger.error(f"Database Error: {e}")
            raise e


def delete_boxer(self, boxer_id: int) -> None:
    """
    Deletes a boxer from the database by their ID. 

    Args:
        boxer_id (int): the ID of the boxer to delete 
    
    Raises: 
        Value Error: If the boxer ID is invalid or the boxer is not found. 
        sqlite3.Error: If a database error occurs 
    """
    logger.info(f"Deleting boxer with ID: {boxer_id}")

    if not isinstance(boxer_id, int) or boxer_id < 0: 
        logger.error(f"Invalid Boxer ID: {boxer_id}. Must be a non-negative integer")
        raise ValueError(f"Invalid Boxer ID: {boxer_id}. Must be a non-negative integer.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Boxer with ID {boxer_id} deleted successfully.")

    except sqlite3.Error as e:
        logger.error(f"Database Error: {e}")
        raise e


def get_leaderboard(self, sort_by: str = "wins") -> List[dict[str, Any]]:
    """
    Retrieves the leaderboard of boxers, sorted by wins or win percentage. 

    Args:
        sort_by (str, optional): the sorting criteria ("wins" or "win_pct"). Defaults to "wins"

    Returns:
        List[dict[str, Any]]: A list of boxer dictionaries, sorted by the specied criteria. 
    
    Raises:
        ValueError: If the sort_by parameter is invalid.
        sqlite3.Error: If a database error occurs. 
    """
    logger.info(f"Getting leaderboard, sorted by: {sort_by}")

    if sort_by not in ["wins", "win_pct"]:
        logger.error(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by paramater: {sort_by}")
    
    
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        logger.info("Leaderboard retrieved successfully.")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """
    Retrieves a boxer from the database by their ID

    Args:
        boxer_id(int): The ID of the boxer to retrieve.

    Returns:
        Boxer: The Boxer object with the specified ID
    
    Raises:
        ValueError: If the boxerID is invalid or the boxer is not found. 
        sqlite3.Error: If a database error occurs 
    """
    logger.info(f"Getting boxer by ID: {boxer_id}")

    if not isinstance(boxer_id, int) or boxer_id < 0: 
        logger.error(f"Invalid boxer ID: {boxer_id}. Must be a non-negative integer.")
        raise ValueError(f"Invalid boxer ID: {boxer_id}. Must be a non-negative integer.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Boxer with ID {boxer_id} retrieved successfully.")
                return boxer
            else:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database Error: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """
    Retrieves a boxer from the database by their name. 
    
    Args:
        boxer_name (str): The name of the boxer to retrieve.

    Returns:
        Boxer: The Boxer object with the specified name.

    Raises:
        ValueError: If the boxer name is invalid or the boxer is not found.
        sqlite3.Error: If a database error occurs
    """
    logger.info(f"Getting boxer by name: {boxer_name}")

    if not isinstance(boxer_name, str) or not boxer_name:
        logger.error(f"Invalid boxer name: {boxer_name}. Must be a non-empty string.")
        raise ValueError(f"Invalid boxer name: {boxer_name}. Must be a non-empty string.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Boxer '{boxer_name}' retrieved successfully.")
                return boxer
            else:
                logger.error(f"Boxer '{boxer_name}' not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """
    Calculates the weight class of a boxer based on their weight.

    Args:
        weight (int): The weight of the boxer in pounds.

    Returns:
        str: The weight class of the boxer.

    Raises:
        ValueError: If the weight is invalid.
    """
    logger.info(f"Calculating weight class for weight: {weight}")

    if not isinstance(weight, int) or weight < 0:
        logger.error(f"Invalid Weight: {weight}. Must be a non-negative integer.")
        raise ValueError(f"Invalid Weight: {weight}. Must be a non-negative integer.")

    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid Weight: {weight}. Weight must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    logger.info(f"Weight Class Calculated: {weight_class}")
    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    Updates the fight statistics (fights and wins) of a boxer in the database.

    Args:
        boxer_id (int): The ID of the boxer to update.
        result (str): The result of the fight ('win' or 'loss').

    Raises:
        ValueError: If the boxer ID is invalid, the result is invalid, or the boxer is not found.
        sqlite3.Error: If a database error occurs.
    """
    logger.info(f"Updating boxer stats for ID: {boxer_id}, result: {result}")


    if not isinstance(result, str) or result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    if not isinstance(boxer_id, int) or boxer_id < 0:
        logger.error(f"Invalid boxer ID: {boxer_id}. Must be a non-negative integer.")
        raise ValueError(f"Invalid boxer ID: {boxer_id}. Must be a non-negative integer.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Boxer stats updated successfully for ID: {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise e
