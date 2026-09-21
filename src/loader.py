__all__ = ['load_config', 'load_entrances', 'load_spoiler', 'load_world']

# from pathlib import Path - all references to file_path and folder_path are Path objects from that pathlib.
import yaml

TYPE_ASSURANCE_CONFIG = {
    "ignore-entrances-types": [],
    "entrance-whitelist": [],
    "render-mode": "",
    "render-mode-normal-settings": {},
    "render-mode-3d-settings": {},
}

#######################
#### ENTRYPOINTS ######
#######################

# loads a config file at specified URI
def load_config(file_path):
    return assure_types(yml_file_loader(file_path), TYPE_ASSURANCE_CONFIG)

# Loads entrances.yml at specified URI
def load_entrances(file_path):
    return yml_file_loader(file_path)
    
# Loads ALL of both worlds' logic files 
def load_world(folder_path):
    return yml_folder_loader(folder_path)

# Loads spoiler log at specified URI
def load_spoiler(file_path):
    return file_loader(file_path, "spoiler log")


########################
###### UTILITY #########
########################

def yml_file_loader(file_path):
    with open(file_path) as file:
        return yaml.safe_load(file)

# recursively loads all .yml files in a folder. Returns a dict of those ymls, processed.    
def yml_folder_loader(folder_path):

    ymls = {}

    for path in list(folder_path.rglob("*.yml")):
        ymls[path] = yml_file_loader(path)

    return ymls
    
# file_description - a description of the file to use in an error message, should accessing the file be a problem.
# example: file_description = "spoiler log".
# returns a list of strings, one for each line
def file_loader(file_path, file_description):
    try:
        with open(file_path, "r") as file:
            contents = file.read().splitlines()
        return contents
    except FileNotFoundError as f:
        print("[OoTMM ER Plotter] File not found: " + file_description + " @ " + str(file_path.absolute()))
        raise f
    except Exception as e:
        print("[OoTMM ER Plotter] An error occurred while trying to open a "+ file_description + " @ " + str(file_path.absolute()), e)
        raise e



# When a yaml is loaded, is interprets types. When a value isn't set, it gets set as None (NoneType)
# This is unfortunate for code expecting a specific type, especially in cases where it's trying
# to load empty lists or dicts
#   loaded_yml = is what you get from yaml.safe_load
#   types = see structure of TYPE_ASSURANCE_CONFIG
def assure_types(loaded_yml, types):
    
    for key, defaultValue in types.items():
        if loaded_yml.get(key) is None:
            loaded_yml[key] = defaultValue
            
    return loaded_yml

