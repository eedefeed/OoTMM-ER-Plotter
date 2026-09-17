__all__ = ['fix_entrances', 'get_incisions']

VOID_AREA_NAMES = ['OOT VOID', 'MM VOID']

# "false" entrances we add to entrances.yml data because it stops unrelated areas
# from merging together into the same node on our graphs due to obscure entrances/exits
# that logic accounts for but entrances.yml doesn't.
# for the "type", we sometimes use a "dummy"-prefixed string. 
# We do this because don't want config.yml to force these to be ignored. (though technically it's still possible)
DUMMY_ENTRANCES = {

    # For spirit temple <> colossus via hands:
    "er_plotter_dummy-OOT_DESERT_COLOSSUS_FROM_TEMPLE_SPIRIT_CHILD_HAND": {
        "game": "oot",
        "type": "dungeon-exit",
        "maps": ["OOT_TEMPLE_SPIRIT", "OOT_COLOSSUS"],
        "areas": ["OOT Spirit Temple Child Hand", "OOT Desert Colossus"],
        "reverse": "er_plotter_dummy-OOT_TEMPLE_SPIRIT_CHILD_HAND_FROM_DESERT_COLOSSUS"
    },
    "er_plotter_dummy-OOT_TEMPLE_SPIRIT_CHILD_HAND_FROM_DESERT_COLOSSUS": {
        "game": "oot",
        "type": "dungeon",
        "maps": ["OOT_COLOSSUS", "OOT_TEMPLE_SPIRIT"],
        "areas": ["OOT Desert Colossus", "OOT Spirit Temple Child Hand"],
        "reverse": "er_plotter_dummy-OOT_DESERT_COLOSSUS_FROM_TEMPLE_SPIRIT_CHILD_HAND"
    },
    
    # These two links aren't needed in MQ but are in vanilla
    "er_plotter_dummy-OOT_DESERT_COLOSSUS_FROM_TEMPLE_SPIRIT_ADULT_HAND": {
        "game": "oot",
        "type": "dungeon",
        "maps": ["OOT_TEMPLE_SPIRIT", "OOT_COLOSSUS"],
        "areas": ["OOT Spirit Temple Adult Hand", "OOT Desert Colossus"],
        "reverse": "er_plotter_dummy-OOT_TEMPLE_SPIRIT_ADULT_HAND_FROM_DESERT_COLOSSUS"
    },
    "er_plotter_dummy-OOT_TEMPLE_SPIRIT_ADULT_HAND_FROM_DESERT_COLOSSUS": {
        "game": "oot",
        "type": "dungeon-exit",
        "maps": ["OOT_COLOSSUS", "OOT_TEMPLE_SPIRIT"],
        "areas": ["OOT Desert Colossus", "OOT Spirit Temple Adult Hand"],
        "reverse": "er_plotter_dummy-OOT_DESERT_COLOSSUS_FROM_TEMPLE_SPIRIT_ADULT_HAND"
    },
    
    # For the boat ride at the tourist hut:
    # In a sense, this isn't a one-way, because you can ride the boat back to the hut.
    # logically, this isn't modelled, so we don't need a dummy reverse exit
    "er_plotter_dummy-MM_BOAT_RIDE_FROM_TOURIST_HUT": {
        "game": "mm",
        "type": "er-plotter-dummy_one-way",
        "maps": ["NONE", "MM_SWAMP"],
        "areas": ["MM Tourist Information", "MM Boat Ride"],
    },
    
    # For exiting night 3 grave via the door:
    "er_plotter_dummy-MM_IKANA_GRAVEYARD_FROM_DAMPE": {
        "game": "mm",
        "type": "er-plotter-dummy_one-way",
        "maps": ["MM_BENEATH_GRAVEYARD_DAMPE", "MM_GRAVEYARD"],
        "areas": ["MM Beneath The Graveyard Night 3", "MM Ikana Graveyard"],
    }
}

# adjusts entrances.yml to fix issues that we would otherwise get.
# (much of the commented code was for when graph nodes and edges were based solely on entrances.yml. Now we use world data, which means less manual/exceptional fixing)
def fix_entrances(entrances):
    
    # Add dummy entrances between areas. These entrances exist in logic but not in entrances.yml.
    entrances.update(DUMMY_ENTRANCES)

    for entrance_id, ed in entrances.items():
        
        # Remove void names, we don't want to represent VOID as a node
        areas = ed.get("areas")
        if areas:
            if areas[0] in VOID_AREA_NAMES:
                areas[0] = areas[1]
            elif areas[1] in VOID_AREA_NAMES:
                areas[1] = areas[0]
                
        # This makes so that each owl warps come from an individual node rather than one "MM SOARING" node.
        if ed["type"] == "one-way-statue": # Assume "maps" and "areas" exist
            owlName = "MM SOARING (" + areas[1] + ")"
            ed["maps"][0] = owlName
            areas[0] = owlName
        

# returns a dict of entrances that haven't been ignored via the config
def active_entrances(entrances, config):
    
    return {
        entrance_id: ed
        for entrance_id, ed in entrances.items()
        if entrance_id in config["entrance-whitelist"] or not ed["type"] in config["ignore-entrances-types"]
    }
    
# Let's imagine that ER first custs up the world, then stitches it back together. Let's detail what those incisions are
# PARAM: entrances: parsed entrances.yml
# RETURN: {dict}
#           - Key: the entrance ID (from entrances.yml)
#           - Value: the logical boundary of the cut: the _areas_ affected
def get_incisions(entrances):
    
    return {
        entrance_id: ed["areas"]
        for entrance_id, ed in entrances.items()
        if len(ed.get("areas", [])) > 1
    }