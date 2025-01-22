
QuantikAI
=========

Play Quantik with an AI

DISCLAIMER: Quantik is a Gigamic game, I am in no way affiliated with Gigamic, played the game at Xmas and wanted to implement it.

The game is playable either between two humans or against a bot.

Free software: MIT license

How to install
---------------

Tested on Linux with Python 3.12

```bash
        git clone git@github.com:Esadruhn/quantikai.git
        cd quantikai
        make install

        # Get help
        python src/quantikai/cli.py --help
        # Same as:
        make cli ARG=--help

        # Play against a bot
        make cli ARG=bot

        # Play again yourself
        make cli ARG=human
```

To use the web interface, do:

```bash
        make dev
```

Timing
------

```bash
        make cli ARG=timer
```

This writes to a file "bot_algo_time.json".

Example json:

```json
{
  "n_iter": 1,
  "montecarlo": {
    "0": 5.7,
    "1": 5.98,
    "2": 4.99,
    "3": 1.01,
    "4": 3.84,
    "5": 0.83,
    "6": 0.71,
    "7": 0.52,
    "8": 0.46,
    "9": 0.49,
    "10": 0.4,
    "11": 0.39,
    "12": 0.26,
    "13": 0.28,
    "14": 0.25
  },
  "minmax": {
    "4": 73.57,
    "5": 88.06,
    "6": 4.77,
    "7": 1.09,
    "8": 0.02,
    "9": 0.0,
    "10": 0.0,
    "11": 0.0,
    "12": 0.0,
    "13": 0.0,
    "14": 0.0
  }
}
```

Next steps
---------------

- test deployment (Docker container, check requirements.txt is ok)
- deployment in prod mode
- see how to improve the Montecarlo algo
- speed improvements on Montecarlo and minmax
- web interface: show the move scores from the algos
- implement a new algo: reinforcement learning agent
