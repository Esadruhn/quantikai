import math
from dataclasses import dataclass

DEFAULT_UCT: float = 1000000
# higher value to increase exploration, lower for exploitation
UCT_CST = 1.5


@dataclass
class MonteCarloScore:
    """Compute values for each node
    for the Monte-Carlo UCT algorithm.
    """

    times_visited: int = 0  # Number of times the node has been visited
    times_parent_visited: int = (
        0  # Number of time any of its parent nodes have been visited
    )
    score: int = 0  # Sum of the iteration rewards
    uct: float = (
        DEFAULT_UCT  # UCT value, that represents a trade-off exploration/exploitation
    )

    def compute_score(
        self,
        uct_cst: float = UCT_CST,
    ) -> float:
        if self.times_visited == 0:
            self.uct = DEFAULT_UCT
        else:
            self.uct = (self.score / self.times_visited) + 2 * uct_cst * math.sqrt(
                2 * math.log(self.times_parent_visited) / self.times_visited
            )
        self.times_parent_visited += 1
        return self.uct

    def to_compressed(self):
        # return only what is necessary to go through the graph, not to keep
        # updating it (would need uct and times_parent_visited)
        return [self.times_visited, self.score]

    @classmethod
    def from_compressed(cls, body):
        return cls(times_visited=body[0], score=body[1])
