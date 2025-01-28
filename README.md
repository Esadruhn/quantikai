
# QuantikAI

Play Quantik with an AI

DISCLAIMER: Quantik is a Gigamic game, I am in no way affiliated with Gigamic, played the game at Xmas and wanted to implement it.

The game is playable either between two humans or against a bot.

My goal here is to get back to programming and test some resolutions methods to create an AI agent to play against.
I want to use minimal domain knowledge of the game (i.e. I am not interested in creating a set of rules to solve the
game).

Free software: MIT license

## How to install

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

        # Deploy the web interface
        # with gunicorn (recommended)
        make devg

        # with Flask
        make dev
```

To use the web interface, do:

```bash
        make dev
```

## Timing

```bash
        make cli ARG=timer
```

This writes to a file "bot_algo_time.json".

Example json:

```json
{
  "n_iter": 10,
  "timestamp": "2025-01-26 16:53:34.563995",
  "montecarlo": {
    "args": {
      "iterations": 1000,
      "use_depth": true
    },
    "0": 3.93,
    "1": 4.16,
    "2": 3.53,
    "3": 2.47,
    "4": 2.54,
    "5": 1.67,
    "6": 1.33,
    "7": 0.9,
    "8": 0.53,
    "9": 0.44,
    "10": 0.23,
    "11": 0.25,
    "12": 0.14,
    "13": 0.15,
    "14": 0.12
  },
  "minmax": {
    "args": {},
    "4": 149.09,
    "5": 33.17,
    "6": 3.56,
    "7": 0.43,
    "8": 0.0,
    "9": 0.0,
    "10": 0.0,
    "11": 0.0,
    "12": 0.0,
    "13": 0.0,
    "14": 0.0
  }
}
```

## Next steps

- Algo improvement: keep working on the MonteCarlo algo
- More tests on the algorithms
- Implement a new algo: reinforcement learning agent

## Implementation notes

### Using the CLI or a web server

Time for the bot to compute the second move (5000 iterations):

- CLI: 18s
- Flask: 23s
- Gunicorn: 18s

I did not investigate more into the app parameters, if I did, would start by taking n measures
for more accurate timings.

### MinMax algorithm

This is a particular case of the minmax algorithm: the reward is binary, either -1 or 1.
So the alpha-beta pruning is straightforward: stop going through child nodes when one of them
has a "win" score for the current player.

### MonteCarlo algorithm

Play the game n_iter times, backpropagate the reward and chose the best move.

Each run is composed of 3 phases:

1. Selection

  Select the next move: if a move has not been tried yet, choose it. Else, use the UCB formula to compute
  each move UCT value and choose the one with the max UCT value.

2. Evaluate the node

  If it is a leaf node (victory or loss), go to the backpropagation step. Else go back to the selection step.

3. Backpropagation

  The reward for a win is equal to the depth of the node (i.e. the number of moves to play to get there).  
  The reward for a loss is 0.
  Update the score of each node that has been visited during this run. If the node is a move by the current player, add the reward.
  If the node is a move by the opponent, then flip the reward: 0 for a win of the current player, number of moves played for a loss.

### Speed bottleneck

A Node contains a board and the next move to play.

How to measure time gains:

- for individual functions: small script using `timeit`

  ```python
    def time_get_possible_moves():
      board.get_possible_moves(args)
    d = timeit.Timer(time_get_possible_moves)
    print(min(d.repeat(20, 100000)))
  ```

- for global algos: `make cli ARG=timer`

#### Board operations: save the board state as a dict of moves vs a list of list

The board operations `Board.play` (with validity and if is win checks) and `Board.get_possible_moves`
are called a lot of times in the algorithms, so any speed gain on these operations end up making a
big difference on the final performance.

I tested two different implementations to represent the board state.

Internal representation of the board as a list of list:

```python
  board = [(Pawns.A, Colors.BLUE), None, None, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, None],
```

Internal representation of the board as a dictionnary of the moves:

```python
  board = {(0,0): ((Pawns.A, Colors.BLUE))}
```

The Montecarlo search is 1.3-1.5x faster with the move dict implementation.
Time for the bot to compute the second move (5000 iterations) deployed with Flask: from
23s to 15s.

#### Optimize the move search by removing redundancies

- On an empty board: only consider one pawn and the 4 cells in the upper right corner
- On a board with one pawn: consider two pawns (the same and one different from the one already on the board) and
  remove redundant cells using symmetries.

This is a great speed-up. I could certainly do more but I do not want to spend too much time on knowledge-based rules
for this exercise.

#### One call to `get_possible_moves` per node then search in the set

In the `_explore_node` function, if it is the first time we check that `parent_node`, then there
is one call to `get_possible_moves`. The possible next moves are saved to the game tree then we save the
resulting board of board + move to play in the parent move.

The next time `_explore_node` is called with this parent node, search in the game tree every node with that board.

##### Result

This is way slower (300s vs 4s to execute `get_best_move` on an empty board). A search in a large set with an
"equal" condition seems to be slower than to compute the possible moves each time

#### Pre-compute the game tree

Pre-compute the game tree and save it to a file.

##### Preliminary result

First try: saving it as is, computed with 50'000 iterations, produces a 1.61Gb file. A naive implementation will not do the job,
this may still be an interesting venue but would require specific developments.

On the top of my head, to reduce the file size:

- require less space to save a node (do not save all values or find a more compact way of writing them), e.g. Ar for an A red pawn.
- save the "levels" (one level = a number of pawns on the board + whether it is player 1 or 2's turn) in different files

Second try: save the data in a more compressed way, computed with 50'000 iterations, save only up to depth 4 included, produces a 355Mb file
naive implementation:

- pre-compute the whole game tree without taking advantage of board symmetries
- with file loaded at each request

#### Node class: save children

Same as the previous method, except that instead of saving the child_board, also save the child moves
Expectations: greater memory usage

TODO

#### Parallel computation

Instead of `n_iter` sequential runs, we might imagine doing `n` runs in parallel for `n_iter` times. We would introduce a random element in the
selection steps, so that the `n` runs are different. This is probably getting closer to a reinforcement learning setup, with a Markov decision process.

## Sources

1. [A Survey of MonteCarlo Search Methods](http://www.incompleteideas.net/609%20dropbox/other%20readings%20and%20resources/MCTS-survey.pdf)
2. [AlphaZero](https://arxiv.org/pdf/1712.01815)
3. [MuZero](https://arxiv.org/pdf/1911.08265)
