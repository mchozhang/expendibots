## COMP30024 AI Project A Report

Wenhao Zhang (970012)	 Yiyang Jin (966255)

#### Problem Formulation

The game *Expendibots* has the following properties: *observable*, *deterministic*, *sequential*, *static*, and *discrete*.

This allows the solution to part A of the game can be seen as a fixed sequence of actions. And therefore, we can transform it into a search problem as follows:

- **State**: Determine by both the number and positions of the tokens on board. The set of possible states is finite. 
- **Actions**: Each stack with *n* tokens have $4n+1$ possible moves 
  - MOVE from its current position $(x, y)$  to $(x \pm \Delta x, y)$ or $(x, y \pm \Delta y)$ with $\Delta x, \Delta y \in \{1,2,…, n\}$, 
  - or take a BOOM action
- **Goal test**: Check whether the board is clear of the black token.
- **Path cost**: Every single step cost 1, so the path cost is the number of steps in the path

#### Search Algorithms

We adopted the weighted A* search to solve the problem. A* search is an informed search algorithm that keeps examining the nodes with the least cost estimation.  A* algorithm uses the evaluation function $f(n) = g(n) + h(n)$ to estimate the cost for node $n$ to reach the goal, where $g(n)$ is the cost from the start node to node $n$, and $h(n)$ is the estimated cost for node $n$ to reach the goal. In our implementation, the heuristic function evaluates the remaining number of black token in the current state. Although the A*  introduces a heuristic function to guide the exploration for new states, the search space can still grow exponentially and cause a time and space overhead. To compensate that, we increased the weight of $h(x)$ function by 10 times to seek a balance between the optimality and the efficiency.

###### Benefits: Efficiency and completeness

- **Space efficiency:** With our heuristic, each board states has only one $h(n)$ value regardless of its predecessors, and thus would be visited only once.  As a result, our search space is a tree instead of a graph as only new board states will be saved and evaluated. Therefore, the cost of space would be largely reduced.
- **Time efficiency:**  To increase the computation speed, we increased the weight of the heuristic function by 10 times to prioritize the states that are closer to the goal. In this way, we pruned away some nodes that are less likely to reach the goal and increased the efficiency of the search.
- **Completeness:** As our search space is a finite tree with non-negative edges, the weight A* will eventually find the solution as long as it exists. 

###### Constraints: Two factors for non-optimality

- **Inadmissible heuristics: **Our heuristic is the number of black tokens remaining on board. Although it is a sensible indication of the estimated cost, it is still an empirical estimation rather than a strictly admissible one. Consider the case where we have two black tokens on board, and they can be eliminated by a BOOM in one move, then the heuristic function would evaluate to 2 while the actual cost is 1. Therefore, there is no guarantee that the estimated cost is always lower than the actual cost. 

  The major problem with this heuristics is that its value does not decrease unless a BOOM takes place. Hence, the actual solution might boom earlier than the optimal one. Moreover, the agent might have to spend more time exploring different movements as the agent cannot tell their difference until a BOOM occurs. 

- **Weighting for the heuristic function:** The weighted A* search is an optimization for originally A* algorithm that trade-off optimality for speed. The cost of its solution will be no more than ten times the cost of an optimal solution. As a result of the weighting, the states with less black tokens will be evaluated earlier.

#### Influencing Factors of Time and Space 

From the results of the five given test cases, we made a comparison on different perspectives of performance among the A* search,  weighted A* and breadth-first search algorithms:

![Performance-of-algorithms](Performance-of-algorithms.png)

- **Branching**: The maximal branching for a single state indicates the number of possible actions for that state. According to our discussion about the number of possible actions in previous paragraphs, it is primarily affected by the number and position of white tokens which defines the maximal possible moves for a single stack. And the position of black tokens also has an effect on it, as we cannot move to the positions that are occupied by black tokens.

- **Depth**: The depth of the solution node is the cost of the searcing. As we can see from the table, it is positively affected by the number of initial tokens as the increase of the tokens will enlarge the set of possible states of the problem. However, a large number of initial tokens do not necessarily lead to a solution located deep down at the search tree, the position of tokens also matters. Meanwhile, different search strategies will also make a difference in the solution cost. Comparing to the result of the BFS (the optimal solution), the solutions of the A* search and Weighted A* are more expensive, especially for the ones with more complex initial states.

- **Time and space complexity**: In all three searches, the space costs are related to the total number of states explored, while the time costs are related to the nodes visited. Although all three algorithms have a $O(b^d)$ complexity on both time and space in the worst case, the actual performance of A* algorithms is far better than the BFS. For weighted A*, time and space complexity is affected largely by the number of white tokens as it is the major determinant of the branching number.

