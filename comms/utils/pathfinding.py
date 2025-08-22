import heapq


def astar(grid, start, goal):
    """
    A* pathfinding on a 2D grid.
    grid: 2D list of 0=blocked, 1=road
    start: (row, col)
    goal: (row, col)
    Returns: list of (row, col) from start to goal
    """
    rows, cols = len(grid), len(grid[0])
    open_set = [(0, start)]
    came_from = {}
    g = {start: 0}

    def h(p): return abs(p[0] - goal[0]) + abs(p[1] - goal[1])  # manhattan

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return [start] + path[::-1]

        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = current[0] + d[0], current[1] + d[1]
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                neighbor = (nr, nc)
                tentative_g = g[current] + 1
                if tentative_g < g.get(neighbor, 1e9):
                    came_from[neighbor] = current
                    g[neighbor] = tentative_g
                    f = tentative_g + h(neighbor)
                    heapq.heappush(open_set, (f, neighbor))

    return []  # no path
