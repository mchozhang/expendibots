## COMP30024 AI Project A Report

Wenhao Zhang 970012  
Yiyang Jin 966255

### Problem Formulation
The game *Expendibots* has the following properties: *observable*, *deterministic*, *sequential*, *static*, and *discrete*, 
which allow the solution can be seen as a sequence of actions. And therefore, we can transform it into a search problem as follows:

* State:   
The state of the board is determined by the position of token stacks and the number and color of the token in each of those stacks.
We use a dictionary to record the state, in which the key is the stack position, and value is the number and color of tokens, 
empty cells should not be included, so that every state of the board can be uniquely represented.  
For example, the board with 2 black tokens on the upper left corner and 1 white tokens on upper right corner can be represented 
by `{(0, 0): "⚫, 2", (7, 7): "⚪, 1"}`.  
In python, we use a `set` to store the board dictionaries that we have explored to avoid duplicated states, and every state should also
record its parent pointer and the last move it takes, so that we can trace back from the final state and find the path.  

* Actions:  
The valid actions of a state consist of all the moves of movable stacks and booms of every white stack. We use a tuple to represent an action:
    * MOVE: `(n, x, y, dx, dy)`, where n is the number of tokens moved, (x, y) is the start position, and (dx,dy) is the destination.
    * BOOM: `(0, x, y, 0, 0)`, where x, y is the position of the stack that booms.  

* Goal test: Check whether the board is clear of the black token.
* Path cost: Every single step cost 1, so the path cost is the number of steps in the path

### Search Algorithms: Weighted A* Search
We adopted the weighted A* search to solve the problem. A* search is an informed search algorithm that keeps examining the
nodes with the least cost estimation.  A* algorithm uses the evaluation function $f(n) = g(n) + h(n)$ to estimate the cost
for node $n$ to reach the goal, where $g(n)$ is the cost from the start node to node $n$, and $h(n)$ is the estimated cost
for node $n$ to reach the goal.  

#### Heuristic Function
In our implementation, the heuristic function returns the remaining number of black cells at the current state. In practice,
the cost $g(n)$ can easily get greater than $h(n)$, which makes heuristic value not significant enough to guide the search,
therefore we use weighted A* search with coefficient `10` to enhance the heuristic function $f(n) = g(n) + 10·h(n)$.

#### Benefits: complexity and completeness 
* Space Complexity and Time Complexity:    
Technically in the worst case, both of the space complexity and time complexity can be $O(b^d)$, where $b$ is the branching factor,
and $d$ is the path depth. In practice, the heuristic function prunes out most of the branches and way more faster then blind search
and A* search. We'll talk about how much does it improve time and space complexity in next section.

* Completeness:  
As our search space is a finite tree with non-negative edges, the weight A* will eventually find the solution as long as it exists. 

#### Constraints: inadmissible and non-optimal
Apparently, the number of the remaining black cells doesn't promise to be less than the true remaining cost. For example, one boom can
eliminate 10 black cells as long as they are connected. Therefore, it violates the principle $h(n) <= h^*(n)$ for admissible heuristics
and solutions it produce do not promise to be optimal. We address more details of this problem in next section. 

### Influencing Factors of Time and Space 
The following table shows that how much does it improve compared to the Breath First Search and A* search, in which the first
4 row is the given test cases, and the 5th is a more complex mutant of the level-4 test.
![Performance-of-algorithms](Performance-of-algorithms.png)

As the game rule decided, the branching factor is determined by the valid actions of each state, more white cells or more tokens in a stack
will produce more valid actions in one state. As we know the solution produces by BFS is the optimal, so both white cell number and length of the
minimal solution can significantly affect the time and space complexity.

#### Occasions that our algorithm works good
Our heuristic indicates the search to eliminate the black cells as soon as possible, it works good in scenarios that have large amount of
black cells, especially when they are discrete, which usually means difficulty level is higher. As we can see in row 4 and 5 in the table,
that it expands 200 time fewer nodes than BFS, and can solve every test case in 1s. On the other hand, in complex cases, it won't produce optimal 
solutions as BFS does, this is the trade-off that we use optimality to exchange speed.

#### Occasions that our algorithm works poor as BFS
The heuristic only takes effect when a white cell reaches a black cells, which means it works like a blind search before approaching
a black cell. Just like `test-level-1`, this simple task is a white cell booms a black cell, for which the nodes it expands and 
solution path it produces is almost the same as BFS, because the heuristic value won't change before it reaches the black cell. 
However, in simple cases like this even BFS is fast enough to produce result, then our algorithm is totally acceptable.