
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
        quantikai --help

        # Play against a bot
        quantikai bot

        # Play again yourself
        quantikai human

        # Deploy the web interface
        # with gunicorn (recommended)
        make devg

        # with Flask
        make dev
```

To use the web interface, do:

```bash
        make devg
```

FEATURE IN PROGRESS:

To get a better bot (from the web interface), do:

```bash
        quantikai montecarlo --depth=2
        make devg
```

`quantikai montecarlo --depth=2` pre-computes the game tree, going much deeper than the on-the-fly algorithm. The result is then used for the first
2 moves on the board, subsequent moves are calcultaed on the fly.

## Timing

```bash
        quantikai timer
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

#### Montecarlo - pre-compute the game tree

Pre-compute the game tree and save it to files (one file per number of pieces on the board and color to play to keep the files small enough to hold in memory).  
Expected advantage: compute the tree with way more iterations, getting a better result.
The issue is that in that case, we compute every state of the board instead of using symmetries for the first 2 moves. Indeed, the opponent may play anything, so if we compute only non-redundant moves we have to map the other board state to these moves. Otherwise, the increased number of moves to compute (eg 16*4 instead of 3 for the first move) negates the advantage of offline computation.

#### Montecarlo - paralellization

See the biography for running parallel computing for the MonteCarlo method, the simplest is also the fastest: `single-run parallelization`, run n iterations in different processes without sharing data and sum the results.

Significant speed-up with the CLI, but the `multiprocess` library interfers with the gunicorn processes (`multiprocess.dummy` is worse than) so it needs more work to use it with the web app.

10'000 iterations, algo time per number of pawns on the board:

```json
    "0": 16.65,
    "1": 14.92,
    "2": 13.11,
    "3": 2.9,
    "4": 10.3,
```

10'000 iterations, 5 processes running 2'000 iterations each:

```json
    "0": 4.3,
    "1": 4.96,
    "2": 4.29,
    "3": 1.15,
    "4": 3.07,
```

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

- for global algos: `quantikai timer`

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

Second try:

- save the data in a more compressed way
  - save only the data up to depth = 3
  - save only the bot player moves (i.e. red player, and assume that blue starts)
- 50'000 iterations of the MonteCarlo algorithm (100'000 iterations leads to a process kill)
- consider all possible move (did not remove redundancies) - removing redundancies would necessitate extra code at play time to infer best moves from symetries
- save only up to depth 3 included (for a sequence of play Blue(depth=0), Red(depth=1), Blue(depth=2), Red(depth=3)), produces a 81Mb file
- at move 3, most nodes have not been visited

So to get improvements with the pre-compute method, we need to exploit symetries and possibly do more iterations.

#### Node class: save children

Same as the previous method, except that instead of saving the child_board, also save the child moves
Expectations: greater memory usage

TODO

#### Parallel computation

For the Monte Carlo tree search, there are 3 methods of parallelization:

- leaf parallelization
- root (or single-run) parallelization
- tree parallelization

## Sources

1. [A Survey of MonteCarlo Search Methods](http://www.incompleteideas.net/609%20dropbox/other%20readings%20and%20resources/MCTS-survey.pdf)
2. [Tristan Cazenave, Nicolas Jouandeau. On the Parallelization of UCT. Computer Games Workshop, Jun 2007, Amsterdam, Netherlands. ￿hal-02310186￿](https://hal.science/hal-02310186/document)
3. [Parallel Monte-Carlo Tree Search](https://dke.maastrichtuniversity.nl/m.winands/documents/multithreadedMCTS2.pdf)
4. [AlphaZero](https://arxiv.org/pdf/1712.01815)
5. [MuZero](https://arxiv.org/pdf/1911.08265)
