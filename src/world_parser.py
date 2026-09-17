__all__ = ['parse']

from collections import deque
import os

SYSTEM_AREA_WHITELIST = {
    "OOT SPAWN CHILD",
    "OOT SPAWN ADULT",
    "OOT SONG_TP_FOREST",
    "OOT SONG_TP_FIRE",
    "OOT SONG_TP_WATER",
    "OOT SONG_TP_SHADOW",
    "OOT SONG_TP_SPIRIT",
    "OOT SONG_TP_LIGHT",
    "MM SOARING"
}

# Parses ootmm's logic files to extract the connections between different areas in the game.
# PARAM: {dict} world_list: 
#          - Key: the name of the games ("OOT" and "MM")
#          - Value: a {dict}:
#                     - Key: file URI or an ootmm logic .yml file
#                     - Value: parsed contents of that yml
# RETURN: {dict}. 
#          - Key: area name, modified: namespaced with game name e.g. "OOT my area"
#          - Value: a set of areas to which the KEY is directly connected.
#          Some connections will be one-way, e.g.; A->B but NOT B->A.
def parse(world_list):
    
    game_names = world_list.keys()
    
    # Find system files and their areas
    system_areas = set() # namespaced - areas that we're not allowing outselves to exit to.
    for game_name, game_logic_files in world_list.items():
        for uri, game_logic_file in game_logic_files.items():
            if os.path.basename(uri) == '_system.yml':
                for area in game_logic_file:
                    system_areas.add(namespace_area(area, game_name, game_names))
                    
                    
    forbidden_areas = system_areas - SYSTEM_AREA_WHITELIST # namespaced - areas that we don't process at all
    
    areas_to_exits = {}    
    for game_name, game_logic_files in world_list.items():
        for uri, game_logic_file in game_logic_files.items():
                      
            for area, data in game_logic_file.items():
                
                # Ensure area name is namespaced
                area = namespace_area(area, game_name, game_names)
                
                if area in forbidden_areas:
                    continue
                
                if not areas_to_exits.get(area):
                    areas_to_exits[area] = set()
                                
                for exit in data.get("exits", {}):
                    exit = namespace_area(exit, game_name, game_names)
                    if not exit in system_areas: # We don't care about any path back to a system region
                        areas_to_exits[area].add(exit)

    return areas_to_exits
    
# Makes changes that help us present data better
def fix_world(parsed_world):
    for owl_area in parsed_world["MM SOARING"]:
        parsed_world["MM SOARING (" + owl_area + ")"] = [owl_area]
    
    del parsed_world["MM SOARING"]
    
    
# PARAM: incisions is a dictionary where each value is a list of two areas to disjoin.
# no return, areas_to_exits is modified in place.
def make_incisions(areas_to_exits, incisions):
    for incision in incisions.values():
        
        a, b = incision[0], incision[1]
        
        if b in areas_to_exits[a]:
            areas_to_exits[a].remove(b)
            
        if b in areas_to_exits[a]:
            areas_to_exits[a].remove(b)
            

# returns a DisjointSet
# this process destroys world_structure
def disjoint_set_world(world_structure):
    return DisjointSet(world_structure)
    
# A slightly unusual implementation of a disjoint set.
# The purpose of this data structure is to understand how the world is connected - and where it is disconnected (Disjointed).
# (a world is completely connected but we make incisions in it as per entrances.yml)
class DisjointSet:
    
    # ._nodes is a dict where each key is a node. The value of each node is either a:
    #       - {string}: CHILD. The value is a string that point directly at the child's representative (and never to some intermediary that in N steps points to the parent)
    #       - NOT a {string}: PARENT. The value is a set of all children (including itself)
    # (the type of the value could be used (internally) to test whether it is child or parent)
    # DESTROYS world_structure
    def __init__(self, world_structure):
        disjoint_set = {}
        self._nodes = disjoint_set 
        
        while world_structure:
        
            area, connectedAreas = world_structure.popitem()
            
            # Breadth-first search (to avoid deep recursion vs depth-first)
            queue = deque(connectedAreas)
            
            visited = set(connectedAreas) | {area}
            disjoint_set[area] = visited 
            
            while queue:
                connectedArea = queue.popleft()
                
                # If this connectedArea doesn't in world_structure, we MUST have already processed it
                # ... and it must therefore be in disjoint_set
                # we must therefore subsume node or the parent of that node
                # (No BFS for this node, it's already been explored.)
                if connectedArea not in world_structure:
                    
                    # Let's find the parent of this connectedArea that we've already processed
                    connectedAreaInfo = disjoint_set[connectedArea]
                    
                    if connectedAreaInfo != area:
                    
                        # If connectedAreaInfo is a string, it's a child node and that string is the parent's name
                        if isinstance(connectedAreaInfo, str):
                            oldParent = connectedAreaInfo
                            children = disjoint_set[connectedAreaInfo]
                        else: # otherwise it's the parent node itself
                            oldParent = connectedArea
                            children = connectedAreaInfo
                        
                        # The current area is now the parent, let's steal the old parent's children. And make it our own child
                        visited.update(children)
                        visited.add(oldParent)

                        
                        # Make each child point at the new parent
                        for child in children:
                            disjoint_set[child] = area
                        
                        # Make the old parent point at the new parent
                        disjoint_set[oldParent] = area
                
                # If the connectedArea is in the world_structure, we need to consume it AND its own children
                else:
                    
                    ## BFS through each neighbour
                    for neighbour in world_structure[connectedArea]:
                        if neighbour not in visited:
                            queue.append(neighbour)
                            visited.add(neighbour)
                    
                    # This represents the child node (connectedArea) AS a child node in our dataset
                    disjoint_set[connectedArea] = area # Child nodes link to their parent in disjoint_set
                    del world_structure[connectedArea] # Child nodes have already been processed, no need to keep them in world structure
                    
    def __str__(self):
        return str(self._nodes)

    #get all of a disjoint_set's parents
    def get_parents(self):
        return [
            key
            for key, value in self._nodes.items()
            if not isinstance(value, str)
        ]
    
    # returns the parent of node
    # if node is a parent, returns self
    def get_parent(self, node):
        value = self._nodes[node]
        if isinstance(value, str):
            return value
        return node

    def get_parents_info(self):
        return {
            parent: children
            for parent, children in self._nodes.items()
            if not isinstance(children, str)
        }

     # get a disjoint_set's parent's children. parent MUST be a parent - not a child.
#    def get_children_for_parent(self, parent):
#        return self._nodes[parent]


#################
#### Utility ####
#################

# prefixes a string with an default (assumed) game name, if it hasn't already been prefixed by any game name (in all_game_names)
def namespace_area(area, assumed_game_name, all_game_names):
    if area.startswith(tuple(all_game_names)):
        return area
        
    return assumed_game_name + " " + area


##################
### TEST NOTES ###
##################

# These are good test cases for disjoint_set_world(test_world)

# Basic loop
"""test_world = {
    'AA': ['BB'],
    'BB': ['CC'],
    'CC': ['AA']  
}"""

# 
"""test_world = {
    "AA": {"DD"},
    "BB": {"DD", "EE"},
    "CC": {"EE"},
    "DD": {"EE"},
    "EE": {"BB"},
}"""

# A connects to C connects to B, which may already be a child of A (as long as you process in last to first order)
# This tests your code to make sure A won't become its own parent. (e.g. {..., A: 'A'})
"""test_world = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['B'], 
    'D': []
}"""




