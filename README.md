# OoTMM ER Plotter

This Python script plots a [(network) graph](https://en.wikipedia.org/wiki/Graph_theory) for an [OoTMM world](https://ootmm.com/). This helps with complicated *Entrance Shuffle* configurations where the shape of the world is hard to understand.

These graphs are useful for:
* Navigation during the course of a seed
* Debugging a seed

These graphs tell you information about the whole world - not just what you've discovered so far. **Consider this a spoiler warning**.

These graphs run in a simulation; the nodes automatically move to try to present the graph better. When this isn't enough (and it usually isn't), nodes can be clicked and grabbed. Extra options can be used to control the simulation and to fix nodes in place.

There's also a 3d mode.

The script works by collecting data from:
* Your spoiler log, 
* OoTMM's source code
* Your configuration file

# Installation

There are two ways to install this project

1. Easy way: run this project using the executable
2. Hard way: run the project using python.
3. Very hard way: build it yourself and use the executable. See [BUILD.MD](BUILD.md)

## Executable Installation
1. Download the latest release
2. Unzip the files into a dedicated folder of your choosing

Only the Windows build has been tested.

## Installation for running with python
1. Install the latest version of Python. This project was made with 3.14.7; that version may be more appropriate than the latest version. Versions prior to 3.9 will definitely not work.
2. Download the whole git project and unzip it into its own folder somewhere.

You have two options - install requirements globally or use a virtual environment. Using a virtual environment is simpler but requires loading the virtual environment before using the script. Only virutal environment installation is covered here.

3. Get a CLI window up and ensure you are in the project's root directory
4. Create virtual environment:

```python -m venv venv```

5. Activate virtual environment:

Linux: `source venv/bin/activate`

Windows: `.\venv\Scripts\activate`

6. Install requirements into the virtual environment:

`pip install -r requirements.txt`

**When using this form of installation, the command to start the script starts with `py main.py` instead of `.\ootmm-er-plotter.exe`**

You will need to ensure the virtual environment is active (see step 5) every time you run the script.

# Usage
The script is executed at the command line.

When the script is successfully executed, **your web browser should automatically load a new tab with the graph**.

It is **highly recommended** that you edit your config file to un-ignore entrance types that you have shuffled. Otherwise, details about your world will not be shown.

The "./user/" folder is provided as a way for you to store files, including spoiler logs and config files. You may store these files anywhere you like, including in the project's root directory or elsewhere on the system; the user folder is provided solely as a convenience.

## Generate graph using config.yml
```.\ootmm-er-plotter.exe .\my-spoiler-log.txt```

The location of the spoiler log is required.

## CLI help
```.\ootmm-er-plotter.exe -h```
Shows CLI help.

## Configuration
By default, the CLI loads `.\config.yml`. An additional default config is also supplied: `.\config - bigger ER.yml`.

Config files can be edited, copied, pasted and moved wherever you like.

Documentation for the config file is found within the supplied config files.

The most important thing to configure is what entrances get ignored.

There are a lot of configuration options for how the graph is displayed. The 2D and 3D versions of the graph have different (but mostly the same) settings. This allows you to control your defaults for each graph type. The 2d graph options are underneath `render-mode-normal-settings` and the 3d ones under `render-mode-3d-settings`.

### Loading a config file at a custom location
To load a config file that is not in the default location, use the `-c` (or `--config`) flag, followed by a reference to the file, for example:

```.\ootmm-er-plotter.exe .\my-spoiler.txt -c .\my-custom-config.yml```

## Using Graphs
The right-hand panel has a lot of options for sorting out the graph. The following options are especially useful:

- Under "Nodes" -> "Drag Behavior" > "Fix Node Position". This makes nodes that you have moved stay in place... mostly. You can make this the default behaviour by setting `node_drag_fix` to `true` in your config. This option is duplicated since it is avaialable for both the 2d and 3d graphs.
- Under "Layout Algorithm" there are a few parameters that control the physics of the graph - they are somewhat worth playing with to try to get your graph looking nicer initially. Some parameters may be hidden based on the layout algorithm that was initially loaded when the script was executed. The `layout_algorithm` setting in the config allows you to select the initial algorithm used.

Some graph options available in `config.yml` do not seem to be available via the UI.

# Building
See [BUILD.MD](BUILD.md)

# Acknowledgements

## Gravis
Most of the spectatucular parts of this script come from the gravis library. All this script does is collect and process data then give it to gravis.

## OoTMM
Most of the data source for this script comes from [OoTMM's source code](https://github.com/OoTMM/OoTMM/)

## AI Disclosure

* Overall architecture: created by a human
* `render.py`'s `make_edges()` function's most complex part was created by an AI. This is the part that collects information about edges that are between the same nodes.
* The "disjoint set" design pattern: suggested by an AI; specialised implementation developed by humans
* The BFS pattern: suggested by an AI, implemented by humans
* Debugging was heavily AI assisted
* Other basic snippets of code were asked of AI and editted/used

Overall, the use of AI was light to moderate. AI never had full access to code base, only snippets were pasted into prompts. Mostly it was used in the same manner as one uses a search engine, with much of its answers verified. 

Only 'free' models were used; no payments were made to AI companies.

# Contact
@eedefeed on [OoTMM](https://ootmm.com/) discord.