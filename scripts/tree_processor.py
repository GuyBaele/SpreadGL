from collections import deque


def iterate_tree(clades):
    stack = deque()
    for clade in clades:
        if not stack:
            stack.append(clade)
        while stack[-1]['visited_times'] == 2:
            exchange_branch_information(stack)
        stack.append(clade)
        if stack[-1]['name'] != 'None':
            exchange_branch_information(stack)
    if stack:
        while stack[-1]['visited_times'] == 2:
            exchange_branch_information(stack)


def exchange_branch_information(stack):
    temp = stack.pop()
    # temp['start_location'] = stack[-1]['end_location']
    temp['start_latitude'] = stack[-1]['end_latitude']
    temp['start_longitude'] = stack[-1]['end_longitude']
    stack[-1]['end_time'] = temp['start_time']
    stack[-1]['start_time'] = stack[-1]['end_time'] - stack[-1]['duration']
    stack[-1]['visited_times'] += 1
