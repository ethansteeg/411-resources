import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture
def ring_model():
    """
    Provides a new RingModel instance for each test.
    """

    return RingModel()

@pytest.fixture
def sample_boxer1():
    """
    Provides a sample Boxer instance.
    """

    return Boxer(id=1, name="Boxer 1", weight=160, height=70, reach=72.0, age=25)

@pytest.fixture
def sample_boxer2():
    """
    Provides a second sample Boxer instance.
    """

    return Boxer(id=2, name="Boxer 2", weight=165, height=72, reach=74.0, age=30)

# -------------------------------
# Boxer Management Test Cases
# -------------------------------

def test_enter_valid_boxer(ring_model, sample_boxer1):
    """
    Test adding a valid Boxer to the ring.
    """

    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == "Boxer 1"

def test_enter_non_boxer_type(ring_model):
    """
    Test adding a non-Boxer object raises a TypeError.
    """

    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer'"):
        ring_model.enter_ring("NotABoxer")

def test_enter_boxer_into_full_ring(ring_model, sample_boxer1, sample_boxer2):
    """
    Test that entering a third boxer into the ring raises a ValueError.
    """

    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    with pytest.raises(ValueError, match="Ring is full"):
        ring_model.enter_ring(Boxer(3, "Extra", 160, 70, 72.0, 28))

def test_clear_ring(ring_model, sample_boxer1):
    """
    Test that the ring is cleared after calling clear_ring.
    """

    ring_model.enter_ring(sample_boxer1)
    ring_model.clear_ring()
    assert len(ring_model.ring) == 0

# -------------------------------
# Retrieval Test Cases
# -------------------------------

def test_get_boxers(ring_model, sample_boxer1, sample_boxer2):
    """
    Test retrieving all boxers currently in the ring.
    """
    
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    boxers = ring_model.get_boxers()
    assert len(boxers) == 2
    assert boxers[0].name == "Boxer 1"
    assert boxers[1].name == "Boxer 2"

# -------------------------------
# Fight Logic Test Cases
# -------------------------------

def test_fight_requires_two_boxers(ring_model, sample_boxer1):
    """
    Test that a fight cannot happen unless two boxers are in the ring.
    """

    ring_model.enter_ring(sample_boxer1)
    with pytest.raises(ValueError, match="There must be two boxers"):
        ring_model.fight()

def test_fight_execution(ring_model, sample_boxer1, sample_boxer2, mocker):
    """
    Test that a fight completes and clears the ring.
    """

    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    mocker.patch("boxing.models.ring_model.update_boxer_stats")
    mocker.patch("boxing.models.ring_model.get_random", return_value=0.5)

    winner_name = ring_model.fight()

    assert winner_name in [sample_boxer1.name, sample_boxer2.name]
    assert len(ring_model.ring) == 0

# -------------------------------
# Skill Calculation Test
# -------------------------------

def test_get_fighting_skill(sample_boxer1, ring_model):
    """
    Test that fighting skill is calculated and returns a float.
    """
    
    skill = ring_model.get_fighting_skill(sample_boxer1)
    assert isinstance(skill, float)