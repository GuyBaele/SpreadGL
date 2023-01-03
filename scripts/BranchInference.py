from collections import deque


def iterateTree(clades):
    stack = deque()
    for clade in clades:
        if not stack:
            stack.append(clade)
        while stack[-1]['visited_times'] == 2:
            branchProcessor(stack)
        stack.append(clade)
        if stack[-1]['name'] != 'None':
            branchProcessor(stack)
    if stack:
        while stack[-1]['visited_times'] == 2:
            branchProcessor(stack)


def branchProcessor(stack):
    temp = stack.pop()
    # temp['start_location'] = stack[-1]['end_location']
    temp['start_latitude'] = stack[-1]['end_latitude']
    temp['start_longitude'] = stack[-1]['end_longitude']
    stack[-1]['end_time'] = temp['start_time']
    stack[-1]['start_time'] = stack[-1]['end_time'] - stack[-1]['duration']
    stack[-1]['visited_times'] += 1
