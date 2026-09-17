import sys
if sys.version_info < (3, 9):
    raise RuntimeError("Python 3.9 or newer is required")

import argparse
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='gravis') # It warns about a deprecation. We solve by forcing old version of setuptools in requirements.text

from src import loader
from src import application

URI_ENTRANCES = "./ootmm/data/defs/entrances.yml" # file
URI_WORLD_OOT = "./ootmm/data/world/oot" #folder
URI_WORLD_MM = "./ootmm/data/world/mm" #folder

###########################
#### PARSE CLI ############
###########################

parser = argparse.ArgumentParser(
    prog='OoTMM ER Plotter',
    description='Visualy plots a network graph of an OoTMM seed.',
    epilog='On success, the script will launch a browser tab/window which displays the graph.'
)

parser.add_argument("spoiler_log", help="URI of the spoiler log from which to load entrance data")
parser.add_argument("-c", "--config", help="URI of the 'OoTMM Plotter ER' config file to be used.", default="./config.yml")

# Exits program if -h is called, showing help
args = parser.parse_args() 

#########################
##### DATA LOAD #########
#########################

config = loader.load_config(args.config)

entrances = loader.load_entrances(URI_ENTRANCES)

spoiler = loader.load_spoiler(args.spoiler_log)

# Load all of oot's and mm's logic files 
world = {
    "OOT": loader.load_world(URI_WORLD_OOT),
    "MM":  loader.load_world(URI_WORLD_MM)
}
 
print("Running Script...")
application.run(config, entrances, spoiler, world)
print("Script Execution Finished. Check your web browser for graph render.")


    






