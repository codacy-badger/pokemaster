# `pokemaster` - Get Real, Living™ Pokémon in Python

[![codecov](https://codecov.io/gh/kipyin/pokemaster/branch/develop/graph/badge.svg)](https://codecov.io/gh/kipyin/pokemaster) [![Travis CI](https://img.shields.io/travis/com/kipyin/pokemaster/develop.svg?label=Travis%20CI)](https://travis-ci.com/kipyin/pokemaster) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## What is this?

`pokemaster` lets you create Pokémon
that is native to the core series Pokémon games
developed by Game Freak & Nintendo.

In `pokemaster`, 
everything you get is
what you would expect in the games:
a Pokémon has a bunch of attributes,
knows up to four moves,
can be evolved to another species,
can learn, forget, and remember certain moves,
can use moves to do stuff 
(such as attacking another Pokémon),
can consume certain items,
and much, much more.

## Installation

1. This project uses [`poetry`](https://poetry.eustace.io) to manage dependencies. Install it via
```shell
$ curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
```
2. Clone this repo:
```shell
$ git clone https://github.com/kipyin/pokemaster.git
```
3. Install dependencies using `poetry` (it will spqwn an virtualenv for you):
```shell
$ poetry install -v
```

## Testing

To run tests, use
```shell
$ make test
```
or
```shell
$ poetry run pytest tests/
```

## Basic Usage

To summon a Real, Living™ Pokémon:

```python
>>> from pokemaster import Pokemon
>>> bulbasaur = Pokemon(national_id=1, level=5)
>>> eevee = Pokemon(identifier='eevee')
```
