# Handles overarching architecture of the project
__all__ = ['run']

import re

# spoiler log is a list of strings. Each item is a line of the spoiler log
def get_entrance_swaps(spoiler_log):

    extract = False
    swaps = []
    
    for num, line in enumerate(spoiler_log):
        if extract:
            # empty line marks the end of entrances
            if line == "":
                break
            
            #match both between-the-brackets texts on each line
            match = re.search(r'^.*?\((.*?)\).*?->.*?\((.*?)\)', line)
            
            if not match:
                raise Exception("Failed to parse spoiler log on line [" + str(num + 1) + "] Line content:", line)
            
            swaps.append(match.groups())
        
        # this marks the beginning of entrances
        if line == "Entrances":
            extract = True
            continue
            
    return swaps