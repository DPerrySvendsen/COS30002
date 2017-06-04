'''  PriorityQueue and Path classes for DFS, BSF, Dijkstra and A* searches

Created for HIT3046 AI for Games by Clinton Woodward cwoodward@swin.edu.au

See readme.txt for details.

'''
from heapq import heappush, heappop

class PriorityQueue(object):
    ''' Cost sorted (min-to-max) queue. Equal cost items revert to FIFO order.'''

    def __init__(self):
        self.q = []
        self.i = 0 # default order counter

    def push(self, item, cost):
        '''Add an item and its cost to the queue. '''
        heappush(self.q, (cost, self.i, item))
        self.i += 1

    def pop(self):
        '''Remove the item of lowest cost, or FIFO order if cost equal.
        Returns the item (whatever it is) and the cost as a tuple. '''
        cost, i, item = heappop(self.q)
        return item, cost

    def __len__(self):
        return len(self.q)

    def __str__(self):
        '''Print a sorted view of the queue contents. '''
        return 'pq: ' + str(sorted(self.q))

    def __contains__(self, item):
        return any(item == values[2] for values in self.q)

    def __iter__(self):
        '''Support iteration. This enables support of the "in" operator. '''
        return iter(values[2] for values in self.q)

    def peek(self, item):
        '''Return a tuple of (item, cost) if it exists, without removing. '''
        for values in self.q:
            if values[2] == item:
                return (item, values[0])

    def remove(self, item):
        '''Remove the first item that matches.'''
        for i, values in enumerate(self.q):
            if values[2] == item:
                del self.q[i]
                return


class Path(object):
    ''' Convenient container and converter for route-path information'''
    def __init__(self, graph, route, target_idx, open, closed, steps):
        # keep any data if we are asked
        self.route = route
        self.open = open
        self.closed = closed
        self.target_idx = target_idx
        self.steps = steps
        # Convert dictionary back in to a list of nodes for a path
        if target_idx in route:
            path = []
            curr_idx = target_idx
            while curr_idx != route[curr_idx]:
                path.append(curr_idx)
                curr_idx = route[curr_idx]
            self.result = 'Success! '

            self.result += 'Still going...' if target_idx in open else 'Done!'
            path.append(curr_idx)
            path.reverse()
            self.path = path
            self.path_cost = str(graph.path_cost(path))
            self.source_idx = curr_idx
        else:
            self.result = 'Failed.'
            self.path = []
            self.path_cost = '---'

    def report(self, verbose=2):
        tmp = "%s Steps: %d Cost: %s\n" % (self.result, self.steps, self.path_cost)
        if verbose > 0:
            tmp += "Path (%d)=%s\n"  % (len(self.path), self.path)
        if verbose > 1:
            tmp += "Open (%d)=%s\n"   % (len(self.open), self.open)
            tmp += "Closed (%d)=%s\n"   % (len(self.closed), self.closed)
        if verbose > 2:
            tmp += "Route (%d)=%s\n"   % (len(self.route), self.route)
        return tmp

def SearchDFS(graph, source_idx, target_positions, limit=0):
    ''' Depth First Search. '''
    closed = set() # set - of visited nodes
    route = {} # dict of {to:from} items to find our way home
    open = [] # use a list as a LIFO stack of the current leaf edges
    steps = 0 # if limit
    end = None
    # add the starting source as an edge tuple to self
    open.append( source_idx )
    route[source_idx] = source_idx # to:from
    # search loop
    while len(open):
        steps += 1
        leaf = open.pop() # get the last added (LIFO) edge to investigate
        closed.add(leaf) # set as 'visited'
        if leaf in target_positions:
            end = leaf
            break
        else:
            idxs = graph.get_neighbours(leaf)
            for dest in idxs:
                if dest not in closed and dest not in open:
                    route[dest] = leaf # to:from
                    open.append( dest )
        # stop early?
        if limit > 0 and steps >= limit:
            break
    # return the partial/complete path details
    return Path(graph, route, end, open, closed, steps)

def SearchBFS(graph, source_idx, target_positions, limit=0):
    ''' Breadth First Search. '''
    closed = set() # set - of visited nodes
    route = {} # dict of {to:from} items to find our way home
    open = [] # use a list as a FIFO queue of the current leaf edges
    steps = 0 # if limit
    end = None

    # add the starting source as an edge tuple to self
    open.append( source_idx )
    route[source_idx] = source_idx # to:from
    # search loop
    while len(open):
        steps += 1
        leaf = open.pop(0) # get's the first (FIFO) node to investigate
        closed.add(leaf)
        if leaf in target_positions:
            end = leaf
            break
        else:
            idxs = graph.get_neighbours(leaf)
            for dest in idxs:
                if dest not in closed and dest not in open: # visited
                    route[dest] = leaf # to:from
                    open.append( dest )
        # stop early?
        if limit > 0 and steps >= limit:
            break
    # return the partial/complete path details
    return Path(graph, route, end, open, closed, steps)

def SearchDijkstra(graph, source_idx, target_positions, limit=0):
    ''' Dijkstra Search. Expand the minimum path cost-so-far '''
    closed = set() # set - of visited nodes
    route = {} # dict of {to:from} items to find our way home
    open = PriorityQueue() # priority queue of the current leaf edges
    steps = 0 # if limit
    end = None

    # add starting node, with cost-so-far (G)
    open.push( source_idx, 0.0 )
    route[source_idx] = source_idx # to:from
    # search loop
    while len(open):
        steps += 1
        leaf, cost = open.pop() # get the lowest cost-so-far node to investigate
        closed.add(leaf)
        if leaf in target_positions:
            end = leaf
            break
        else:
            idxs = graph.get_neighbours(leaf)
            for dest in idxs:
                if dest not in closed: # visited
                    cost_f = cost + graph.get_edge(leaf,dest).cost # cost_g
                    if dest in open: # old path to same node?
                        if open.peek(dest)[1] <= cost_f: # if better, keep it
                            continue
                        else: # remove the old, and the new one be added
                            open.remove(dest)
                    route[dest] = leaf # to:from
                    open.push(dest, cost_f )
        # stop early?
        if limit > 0 and steps >= limit:
            break
    # return the partial/complete path details
    return Path(graph, route, end, open, closed, steps)

def SearchAStar(graph, source_idx, target_positions, limit=0):
    ''' A* Search. Expand the minimum path cost-so-far + lowest heuristic cost. '''
    closed = set() # set - of visited nodes
    route = {} # dict of {to:from} items to find our way home
    open = PriorityQueue() # priority queue of the current leaf edges
    steps = 0
    end = None
    target_idx = target_positions[0]
    # add starting node, with F = cost-so-far (G) + heuristic (H)
    open.push(source_idx, graph.cost_h(source_idx, target_idx))
    route[source_idx] = source_idx
    # search loop
    while len(open):
        steps += 1
        leaf, cost_f = open.pop() # get the lowest cost-so-far node to investigate
        closed.add(leaf) # set 'visited'
        if leaf in target_positions:
            end = leaf
        else:
            # use the old cost_f to get the real base cost_g for the path so-far
            cost = cost_f - graph.cost_h(leaf, target_idx)
            # get new children
            idxs = graph.get_neighbours(leaf)
            for dest in idxs:
                if dest not in closed: # visited
                    cost_g = cost + graph.get_edge(leaf, dest).cost # G cost-so-far
                    cost_h = graph.cost_h(dest, target_idx) # H estimated-cost
                    cost_f = cost_g + cost_h
                    if dest in open:
                        if open.peek(dest)[1] <= cost_f:
                            continue
                        else:
                            open.remove(dest)
                    route[dest] = leaf
                    open.push(dest, cost_f)
        # stop early?
        if limit > 0 and steps >= limit:
            break
    # return the partial/complete path details
    return Path(graph, route, end, open, closed, steps)

# A simple dictionary with string keys to each search class type.
search_methods = {
    'DFS':      SearchDFS,
    'BFS':      SearchBFS,
    'Dijkstra': SearchDijkstra,
    'AStar':    SearchAStar,
}