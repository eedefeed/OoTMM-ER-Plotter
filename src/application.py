# Handles overarching architecture of the project
__all__ = ['run']

from collections import Counter

from src import world_parser
from src import spoiler_parser
from src import entrances_parser
from src import render

NO_NAME_COUNT = 0
FORBIDDEN_NAME_VOTES = { # areas are forbidden from voting their wider region to be called these:
    "NONE"
}

# Entrance types that indicate that the first entry in [maps] or [areas] should be a spawnpoint node (different formatting)
SPAWNPOINT_NODE_TYPES = [
    "one-way-song",
    "one-way-statue",
    "spawn-child",
    "spawn-adult"
]

# Entrance types that indicate that the first entry in [maps] or [areas] should be a minor node
MINOR_NODE_AREA0_TYPES = [
    "grotto-exit",
    "indoors-exit",
    "grave-exit"
]

# Entrance types that indicate that the second entry in [maps] or [areas] should be a minor node
MINOR_NODE_AREA1_TYPES = [
    "grotto",
    "grave",
    "indoors",
    "indoors-extra",
    "indoors-telescope"
]
# indoors-special is just sakon's hideout. Ignoring because complicated - let it have big node.

def run(config, entrances, spoiler, world):
    
    # Custom modify entrances, then work out where ER can make incisions to the world
    entrances_parser.fix_entrances(entrances)
    incisions = entrances_parser.get_incisions(
        entrances_parser.active_entrances(entrances, config)
    )

    # Map the logical structure of the world (logic .yml files), and make some adjustments to make the graph nicer
    world_structure = world_parser.parse(world)
    world_parser.fix_world(world_structure)
    
    # Cut the logical structure of the world along ER boundaries
    world_parser.make_incisions(world_structure, incisions)
    
    # Group up (logical) areas that are still connected in some way, even after we've cut up the world
    # These form the nodes of our graph
    disjoint_set_world = world_parser.disjoint_set_world(world_structure)
    node_info = generate_node_info(disjoint_set_world, entrances, config)

    # Figure out how ER has changed the world and then modify our incision data
    # These modified incisions form the edges (lines, arrows) of our graph
    spoiler_swaps = spoiler_parser.get_entrance_swaps(spoiler)
    incisions.update(process_spoiler_swaps(spoiler_swaps, entrances))
    
    # Render the world, using our ER-adjusted incisions to stitch the world back together
    gjgf = render.make_gjgf(node_info, disjoint_set_world, incisions)
    render.render(gjgf, config)

# Consolidates and generates information for each node
def generate_node_info(disjoint_set_world, entrances, config):
    
    all_node_info = {
        parent: {
            "game":  parent.partition(" ")[0], # I don't really like picking it up from area's namespace. It seems flimsy. But it's the easiest access to game we have.
            "name":  determine_node_name(children, entrances),
            "type": "normal", # will be overwritten later if neccesary 
            "child_nodes": children
        }
        for parent, children in disjoint_set_world.get_parents_info().items()
    }
    
    # Go through entrances to find nodes that we can change the type of (render.py looks at type when styling nodes)
    for ed in entrances.values():
        
        if not ed.get("type") or ed["type"] in config["ignore-entrances-types"]:
            continue
            
        if ed["type"] in SPAWNPOINT_NODE_TYPES:
            all_node_info[
                disjoint_set_world.get_parent(ed["areas"][0])
            ]["type"] = "spawnpoint"
            
        elif ed["type"] in MINOR_NODE_AREA0_TYPES:
            #print("--- Area0 minor ---")
            #print(disjoint_set_world.get_parent(ed["areas"][0]))
            #print(ed["areas"])
            all_node_info[
                disjoint_set_world.get_parent(ed["areas"][0])
            ]["type"] = "minor"
            
        elif ed["type"] in MINOR_NODE_AREA1_TYPES:
            #print("--- Area1 minor ---")
            #print(disjoint_set_world.get_parent(ed["areas"][1]))
            #print(ed["areas"])
            all_node_info[
                disjoint_set_world.get_parent(ed["areas"][1])
            ]["type"] = "minor"

    return all_node_info

# Use whatever information we have about the nodes to try to figure out the best name for a node.
# A variety of methods are used. If one method fails, the next method is tried
# METHOD 1  - Special handling for telescopes, hyrule market and clock town
# METHOD 2  - nodes' areas vote on names
# METHOD 3+ - fallback methods, as documented in the code
def determine_node_name(node_areas, entrances):
    
    # Nodes can have multiple areas. Lets get these areas to 'vote' on what they think the name of the node should be
    votes = Counter()
    for ed in entrances.values():
        
        if not ed.get("maps"):
            continue
        
        for i, area in enumerate(ed.get("areas", [])):
            if area in node_areas:
                
                # Special handling for telescopes (not 100% sure of this code)
                if ed["type"] == "indoors-telescope":
                    return area
                    
                map_name = ed["maps"][i]
                                
                # special handling for hyrule market and clock town submaps
                if map_name in ("MM_CLOCK_TOWN", "OOT_MARKET") and ed.get("submaps"):
                    return map_name + " " + ed["submaps"][i]
                
                if not map_name in FORBIDDEN_NAME_VOTES:
                    votes[map_name] += 1
    
    # If any votes have been cast, return the most popular
    if votes:
        return votes.most_common(1)[0][0]
        
    # Fallback option 1: if there's only one area, then call it that.
    if len(node_areas) == 1:
        return next(iter(node_areas))
        
    # Fallback option 2: children represented anywhere in entrance.yml are probably good name candidates because they're likely to be named after the area
    priority_children = set()
    for ed in entrances.values():
        for area in ed.get("areas", []):
            if area in node_areas:
                priority_children.add(area)
                
    if len(priority_children) == 1:
        return next(iter(priority_children))
        
    # Fallback option 3: see if the areas have a common name between them - some common words at the start of their name. (minimum 3)
    words = [area.split() for area in node_areas]
    prefix = []
    for group in zip(*words):
        if len(set(group)) != 1:
            break
        prefix.append(group[0])
    
    if len(prefix) >= 3:
        return " ".join(prefix)

    # Final fallback: 
    global NO_NAME_COUNT
    NO_NAME_COUNT += 1
    fallback_name = "NO NAME " + str(NO_NAME_COUNT)
    print("[ER_PLOTTER]: unable to name a node. Assigned a fallback name: " + fallback_name + " ; areas: " + str(node_areas))
    return fallback_name

# entrances matches the format of entrances.yml    
# spoiler swaps is in the form [(entrance_id_1, entrance_id_2), (entrance_id_3, entrance_id_4)]
# where entrance_id_x matches entrance.yml's keys 
# returns in the form {
#   entrance_id_x: [area1, area2]
def process_spoiler_swaps(spoiler_swaps, entrances):
    
    return {
        exit: [entrances[exit]["areas"][0], entrances[enter]["areas"][1]]   
        for exit, enter in spoiler_swaps
    }

        
        