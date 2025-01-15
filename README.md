
QuantikAI
=========

Play Quantik with an AI

DISCLAIMER: Quantik is a Gigamic game, I am in no way affiliated with Gigamic, played the game at Xmas and wanted to implement it.

The game is playable either between two humans or against a bot.


* Free software: MIT license

How to install
---------------

Tested on Linux with Python 3.12

```bash
        git clone git@github.com:Esadruhn/quantikai.git
        cd quantikai
        make install

        # Get help
        python src/quantikai/cli.py --help

        # Play against a bot
        python src/quantikai/cli.py bot

        # 2 humans
        python src/quantikai/cli.py human
```

Timing
------

```bash
        # Play against a bot
        python src/quantikai/cli.py timer
```
for 10 iterations of bot vs bot, shows average time