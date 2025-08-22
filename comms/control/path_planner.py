from utils.pathfinding import astar


def plan_path(grid, start, goal):
    """
    Plan path from start → goal using A*.
    Args:
        grid (list[list[int]]): 2D grid (0=free, 1=blocked).
        start (tuple): (row,col)
        goal (tuple): (row,col)
    Returns:
        list[tuple]: path as list of (row,col) cells
    """
    return astar(grid, start, goal)
