import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage a boxing ring where up to two boxers can fight.
    """

    def __init__(self):
        """
        Initializes the object RingModel with an empty ring.
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight between two boxers in a ring.

        Uses a logistic function to determine the winner based on their skill difference.

        Returns:
            str: The name of the winning boxer.
        
        Raises:
            ValueError: If fewer than two boxers are in the ring.
        """
        logger.info("Fight requested.")

        if len(self.ring) < 2:
            logger.error("Cannot start fight: not enough boxers in the ring.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Boxers ready: {boxer_1.name} vs {boxer_2.name}.")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        logger.debug(f"Skill 1: {skill_1}, Skill 2: {skill_2}, Delta: {delta:.2f}.")
        logger.debug(f"Normalized delta: {normalized_delta:.4f}, Random number: {random_number:.4f}.")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"Winner: {winner.name}, Loser: {loser.name}.")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()
        logger.info("Ring cleared after fight.")

        return winner.name

    def clear_ring(self):
        """
        Clears all boxers from the ring.
        """
        if not self.ring:
            logger.info("Ring already empty.")
            return
        logger.info("Clearing the ring.")
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add.

        Raises:
            TypeError: If the input is not a Boxer.
            ValueError: If the ring already has two boxers.
        """
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'.")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning("Cannot add boxer: ring is already full")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """
        Returns the list of boxers currently in the ring.

        Returns:
            List[Boxer]: A list of boxers.
        """
        if not self.ring:
            logger.debug("No boxers currently in the ring")
        else:
            logger.debug(f"{len(self.ring)} boxer(s) found in the ring")

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates the fighting skill of a boxer using a custom formula.

        Args:
            boxer (Boxer): The boxer whose skill is to be calculated.

        Returns:
            float: The computed fighting skill score.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug(f"Calculated skill for '{boxer.name}': {skill:.2f}.")

        return skill