from collections import deque


def iterate_tree(branches):
    stack = deque()
    for branch in branches:
        if not stack:
            stack.append(branch)
        while stack[-1]['visited_times'] == 2:
            calculate_parent_edge_time(stack)
        stack.append(branch)
        if stack[-1]['end_time'] != 0.0:
            calculate_parent_edge_time(stack)
    if stack:
        while stack[-1]['visited_times'] == 2:
            calculate_parent_edge_time(stack)


def calculate_parent_edge_time(stack):
    temp = stack.pop()
    stack[-1]['end_time'] = temp['start_time']
    stack[-1]['start_time'] = stack[-1]['end_time'] - stack[-1]['length']
    stack[-1]['visited_times'] += 1
