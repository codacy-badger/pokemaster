#!/usr/bin/env python3
from functools import partial

import attr
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from pokemaster.pokemon import PRNG, Gender, Pokemon, Stats, Trainer, get_move

# Given a seed, the PRNG should have the exact same behavior.
# The seed and the results are from the following link:
# https://www.smogon.com/ingame/rng/pid_iv_creation#pokemon_random_number_generator


def test_prng_default_seed_is_0():
    prng = PRNG()
    assert prng() == 0


@given(st.integers())
def test_prng_sanity(seed):
    prng = PRNG(seed)
    value = ((0x41C64E6D * seed + 0x6073) & 0xFFFFFFFF) >> 16
    assert prng() == value


def test_next_5():
    prng = PRNG(0x1A56B091)
    assert prng.next(5) == [0x01DB, 0x7B06, 0x5233, 0xE470, 0x5CC4]


def test_reset_prng():
    prng = PRNG()
    assert prng() == 0
    prng.next(10)
    prng.reset()
    assert prng() == 0


def test_pid_ivs_creation():
    prng = PRNG(0x560B9CE3)
    assert (0x7E482751, 0x5EE9629C) == prng.create_pid_ivs(method=2)


def test_trainer_sanity():
    Trainer.prng = PRNG()
    t = Trainer('Kip')
    assert t.id == 0
    assert t.secret_id == 59774


@pytest.fixture
def bulbasaur():
    """Instantiate a Bulbasaur.

    According to the PID, this is a male bulbasaur with Overgrow ability,
    hardy nature, and not shiny.
    """
    prng = PRNG()
    Pokemon.prng = prng
    Trainer.prng = prng
    kip = Trainer('Kip')
    # kip.id = 0
    # kip.secret_id = 59774
    bulbasaur = Pokemon(1)
    # bulbasaur.pid = 833639025
    # bulbasaur.ivs = 2948981452
    bulbasaur.trainer = kip
    yield bulbasaur


# PID related mechanisms


def test_bulbasaur_ids(bulbasaur):
    assert bulbasaur.trainer.id == 0
    assert bulbasaur.trainer.secret_id == 59774
    assert bulbasaur._pid == 833639025
    assert bulbasaur._ivs == 2948981452


def test_pokemon_gender(bulbasaur):
    assert bulbasaur.gender == Gender.MALE  # male
    nidoran_f = Pokemon('nidoran-f')
    nidoran_f.trainer = bulbasaur.trainer
    assert nidoran_f.gender == Gender.FEMALE
    nidoran_m = Pokemon('nidoran-m')
    nidoran_m.trainer = bulbasaur.trainer
    assert nidoran_m.gender == Gender.MALE
    magnemite = Pokemon('magnemite')
    magnemite.trainer = bulbasaur.trainer
    assert magnemite.gender == Gender.GENDERLESS


def test_pokemon_ablity(bulbasaur):
    assert bulbasaur.ability.identifier == 'overgrow'


def test_pokemon_nature(bulbasaur):
    assert bulbasaur.nature.identifier == 'hardy'


def test_pokemon_shininess(bulbasaur):
    """See https://bulbapedia.bulbagarden.net/wiki/Personality_value#Example"""
    assert not bulbasaur.shiny


@pytest.fixture(scope='function')
def garchomp():
    """A Level 78 Garchomp with the following IVs and EVs and an
    Adamant nature:

    +===========+=====+========+=========+========+========+========+=======+
    |           |  HP | Attack | Defense | Sp.Atk | Sp.Def |  Speed | Total |
    +===========+=====+========+=========+========+========+========+=======+
    | Base stat | 108 |   130  |    95   |   80   |   85   |   102  |  600  |
    +-----------+-----+--------+---------+--------+--------+--------+-------+
    |    IV     |  24 |    12  |    30   |   16   |   23   |     5  |  110  |
    +-----------+-----+--------+---------+--------+--------+--------+-------+
    |    EV     |  74 |   190  |    91   |   48   |   84   |    23  |  510  |
    +-----------+-----+--------+---------+--------+--------+--------+-------+
    |   Total   | 289 |   278  |   193   |  135   |  171   |   171  |       |
    +-----------+-----+--------+---------+--------+--------+--------+-------+

    https://bulbapedia.bulbagarden.net/wiki/Statistic#Example_2
    """
    Pokemon.prng = PRNG(0x1C262455)
    garchomp = Pokemon('garchomp', pid_method=4, level=78)
    garchomp.effort_values.set(
        hp=74,
        attack=190,
        defense=91,
        special_attack=48,
        special_defense=84,
        speed=23,
    )
    yield garchomp


# TestPokemonStats


def test_ivs():
    """Seed and IVs can be found in:
    https://sites.google.com/site/ivtopidapplet/home
    """
    Pokemon.prng = PRNG(0x35CC77B9)
    weedle = Pokemon(13)
    assert weedle._pid == 0xEF72C69F
    assert weedle._ivs == 0xFFFFFFFF


def test_iv(garchomp):
    assert garchomp.iv.astuple() == (24, 12, 30, 16, 23, 5)


def test_base_stats_sanity(garchomp):
    for stat in garchomp.base_stats.astuple():
        assert stat != 0


def test_calculate_stats(garchomp):
    calculated_stats = garchomp._calculate_stats()
    assert calculated_stats.hp == 289
    assert calculated_stats.attack == 278
    assert calculated_stats.defense == 193
    assert calculated_stats.special_attack == 135
    assert calculated_stats.special_defense == 171
    assert calculated_stats.speed == 171


# Test Pokémon Level Up


def test_experience(garchomp):
    assert garchomp.experience == 593_190


# 616_298 - 593_190 = 23_108
@given(st.integers(0, 23_108))
def test_pokemon_gaining_experience_without_leveling_up(exp):
    # Since the fixture only run once per test, not once per example,
    # we have to do manual setups. Also, the EV doesn't matter when
    # testing the exoeriences.
    garchomp = Pokemon('garchomp', level=78)
    garchomp.experience += exp
    assert garchomp.experience == 593_190 + exp
    assert garchomp.level == 78


def test_pokemon_gaining_exact_experience_to_level_up():
    garchomp = Pokemon('garchomp', level=78)
    garchomp.experience += 23_108
    assert garchomp.experience == 616_298
    assert garchomp.level == 79


# 640_000 - 593_190 = 46_810
@given(st.integers(23_108, 46_810))
def test_pokemon_gaining_experience_more_than_needed_to_level_up(exp):
    garchomp = Pokemon('garchomp', level=78)
    garchomp.experience += exp
    assert garchomp.experience == 593_190 + exp
    assert garchomp.level == 79


# 1_250_000 - 593_190 = 656_810
# Using @given will make hypothesis fuss about how slow the test is.
@pytest.mark.parametrize('exp', [656_810, 656_811, 1_656_810])
def test_pokemon_gaining_experience_to_get_to_level_100(exp):
    garchomp = Pokemon('garchomp', level=78)
    garchomp.experience += exp
    assert garchomp.experience == 1_250_000
    assert garchomp.level == 100


# TestPokemonMoves


def test_get_move():
    assert get_move(1).identifier == 'pound'
    assert get_move('pound').id == 1
    with pytest.raises(TypeError):
        get_move(b'pound')


@settings(max_examples=20)
@given(st.text())
def test_invalid_names_raise_error(random_move_name):
    with pytest.raises(ValueError):
        get_move(random_move_name)


def test_pokemon_initial_moves(bulbasaur):
    assert list(map(lambda x: x.id, bulbasaur.moves)) == [45, 33]


def test_learnable_moves(bulbasaur):
    assert bulbasaur.learnable(get_move('cut'))
    assert not bulbasaur.learnable(get_move('pound'))
