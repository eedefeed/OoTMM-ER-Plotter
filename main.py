import sys
if sys.version_info < (3, 9):
    raise RuntimeError("Python 3.9 or newer is required")

import os
import sys
from pathlib import Path
import argparse
import traceback
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='gravis') # It warns about a deprecation. We solve by forcing old version of setuptools in requirements.text

from src import loader
from src import application

PRINT_PREFIX = "[OoTMM ER Plotter] "

###########################
#### PARSE CLI ############
###########################

parser = argparse.ArgumentParser(
    prog='OoTMM ER Plotter',
    description='Visualy plots a network graph of an OoTMM seed.',
    epilog='On success, the script will launch a browser tab/window which displays the graph.'
)

parser.add_argument("spoiler_log", help="URI of the spoiler log from which to load entrance data", nargs='?')
parser.add_argument("-c", "--config", help="URI of the 'OoTMM Plotter ER' config file to be used. By default, it loads config.yml from the directory where the script is located.")
parser.add_argument("-d", "--debug", help="Enables more verbose debugging output", action="store_true")
parser.add_argument("-f", "--file", help="The URI where the graph will be saved. By default it will save to ootmm_er_plotter_graph.htm in the directory where the script is located")

# Exits program if -h is called, showing help
args = parser.parse_args() 

#########################
###### PROMPTS ##########
#########################

# If the user didn't supply a spoiler log URI, prompt for one.
if args.spoiler_log is None:
    
    print(PRINT_PREFIX + "Please supply a URI reference to an OoTMM spoiler log. On some OSes, you can drag and drop a file into this prompt. Press enter to continue. (You can skip this step by supplying the spoiler log URI when you execute this script.)") #TODO
    
    user_spoiler_input = input(PRINT_PREFIX + "Spoiler log URI: ").strip("'")
    
    # Insist on input - this workaround stops the user from seeing an unintuitive "no permission" file access error if they enter nothing.
    while user_spoiler_input == "":
        print(PRINT_PREFIX + "Please supply a valid URI reference to an OoTMM spoiler log")
        user_spoiler_input = input(PRINT_PREFIX + "Spoiler log URI: ").strip("'")
    
    # Aid Windows users by handling Windows' tendancy to add quotes when dragging and dropping into console
    if os.name == "nt":
        args.spoiler_log = user_spoiler_input.strip('"')
    else :
        args.spoiler_log = user_spoiler_input
    
#########################
#### URI Resolving ######
#########################

## find the location of the executable
if getattr(sys, 'frozen', False): # environment: bundle/executable (via pyinstaller)
    script_path = Path(sys.executable)
else: # environment: normal (via "py main.py")
    script_path = Path(__file__)
    
script_dir = script_path.resolve().parent

# Get data source paths relative to the executable, not the current working directory.
path_entrances = script_dir / Path("./ootmm/data/defs/entrances.yml") # file
path_world_oot = script_dir / Path("./ootmm/data/world/oot") #folder
path_world_mm  = script_dir / Path("./ootmm/data/world/mm") #folder

# For command-line URIs, default values are relative to the executable, but user-provided values are relative to the current working directory.
if args.config is None:
    path_config = script_dir / Path("./config.yml")
else:
    path_config = Path(args.config)
    
if args.file is None:
    path_save_graph = script_dir / Path("./ootmm_er_plotter_graph.htm")
else:
    path_save_graph = Path(args.file)
    
# No special handling for spoiler log path.

##############################
##### LOAD DATA AND RUN ######
##############################

try:
    print(PRINT_PREFIX + "Loading Data...")

    config = loader.load_config(path_config)

    entrances = loader.load_entrances(path_entrances)

    spoiler = loader.load_spoiler(Path(args.spoiler_log))

    # Load all of oot's and mm's logic files 
    world = {
        "OOT": loader.load_world(path_world_oot),
        "MM":  loader.load_world(path_world_mm)
    }
    
except Exception as e:
    print(PRINT_PREFIX + "Unable to load all required files. Run this script from the command line with -d for more verbose debugging output.")
    if args.debug:
        traceback.print_exc()
    else:
        print(e)
        
else:
    print(PRINT_PREFIX + "Processing...")
    raw_html = application.run(config, entrances, spoiler, world)
    print(PRINT_PREFIX + "Graph succesfully rendered. Check your web browser.")
    
    ## SAVE GRAPH FILE  
    write = True
    if path_save_graph.exists():
        ui = input(PRINT_PREFIX + "File at '" + str(path_save_graph.absolute()) + "' already exists, overwrite? y/n: ")
        if not ui in ('y', 'Y'):
            write = False
        
    if write:
        
        try:
            print(PRINT_PREFIX + "Saving Graph.")
            path_save_graph.write_text(raw_html, encoding="utf-8")
            
        except Exception as e:
            print(PRINT_PREFIX + "Unable to save file. Run this script from the command line with -d for more verbose debugging output.")
            if args.debug:
                traceback.print_exc()
            else:
                print(e)
            
    else:
        print(PRINT_PREFIX + "Graph not saved")
    
input(PRINT_PREFIX + "Press [Enter] to exit.")


    






