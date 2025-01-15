
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
        pip install -r requirements_dev.txt
        pip install -e .
        python src/quantikai/cli.py --help

        # Play against a bot
        python src/quantikai/cli.py bot

        # 2 humans
        python src/quantikai/cli.py human
```

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

- [Cookiecutter](https://github.com/audreyr/cookiecutter)
- [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage)

Timing
------

Timeit - 10 iterations of botvsbot: 15.683639091999794s - commit testais 5a4e9f2