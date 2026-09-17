__all__ = ['render', 'make_gjgf']

import gravis
from itertools import cycle
from collections import defaultdict

# Functions that we use to generate our graphs
# KEY: value retrieved from config yml's "render-mode" variable
# VALUE: function to use
RENDER_MODE_FUNCTIONS = {
    "normal": gravis.vis,
    "3d": gravis.three
}

GAME_COLOURS = {
    "OOT": {
        "dark": '#a00004',
        "light": '#ffaaa5'
    },
    "MM": {
        "dark": '#45256e',
        "light": '#d2a8ff'
    }
}

NODE_FORMATTING = {
    game : {
        "normal": {
            "color": colours["dark"]
        },
        "spawnpoint": {
            "shape": "rectangle",
            "border_size": 2,
            "color": colours["light"],
            "border_color": colours["dark"],
            "label_size": '15%'
        },
        "minor": {
            "opacity": 0.75,
            "label_size": '9.5%',
            "size": 7,
            "label_color": '#222222',
            "color": colours["light"],
        },
    }
    for game, colours in GAME_COLOURS.items() # make for each game
}

# HTML
HTML_HOVER_TAG = 'div'
HTML_HOVER_ATTRIBUTES = 'style="font-size: 150%; font-family: \'Lucida Console\', Monaco, monospace"'

HTML_CLICK_TAG = 'div'
HTML_CLICK_ATTRIBUTES = 'style="font-size: 120%"'

HTML_LIST_CONTAINER_TAG = 'ul'
HTML_LIST_CONTAINER_ATTRIBUTES = 'style="margin: 0; padding: 0 0 0 1em; list-style: \'{marker}\' outside; display:flex; flex-wrap: wrap;"' 
HTML_LIST_ITEM_TAG = 'li'
HTML_LIST_ITEM_ATTRIBUTES = 'style="margin-right: 2.4em; padding-left: 0.25em; color: #{cycle_colour}"' #display: inline-block; 
HTML_LIST_COLOURS = cycle(['500', '050', '005'])#, '660', '606', '066', '000']) #no grey!

MARKER_AREA = '&#x2756;' #unicode: BLACK DIAMOND MINUS WHITE X
MARKER_ENTRANCE = '&#x1F87A' # unicode: WIDE-HEADED RIGHTWARDS HEAVY BARB ARROW

## These other arrows are good backup options:
# '&#x279C'  HEAVY ROUND-TIPPED RIGHTWARDS ARROW
# '&#x2B72'  RIGHTWARDS TRIANGLE-HEADED ARROW TO BAR
# '&#x1F80A' RIGHTWARDS ARROW WITH LARGE TRIANGLE ARROWHEAD
# '&#x1F872' WIDE-HEADED RIGHTWARDS MEDIUM BARB ARROW

#################################################################################################################

# Renders a gjgf as a (network) graph. use make_gjgf() to make the gjgf
# gjgf spec: https://robert-haas.github.io/gravis-docs/rst/format_specification.html
def render (gjgf, config):
    renderMode = config["render-mode"]
    renderFunc = RENDER_MODE_FUNCTIONS[renderMode]
    renderFuncSettings = config["render-mode-" + renderMode + "-settings"] 

    fig = renderFunc(gjgf, **renderFuncSettings)
    fig.display()

# PARAM: {dict} node_info - matches the output of generate_node_info() in application.py
# PARAM: {DisjointSet} disjoint_set - defined in world_parser.py
# PARAM: {dict} connections - how to connect nodes
#           - Key: {string}: an entrance ID (from entrances.yml) - this, almost arbitrary, value is used as the node ID
#           - Value: {list} of {string}: the two areas to be joined.
# RETURN: {dict} - a gjgf (see: gjgf spec: https://robert-haas.github.io/gravis-docs/rst/format_specification.html)
def make_gjgf(node_info, disjoint_set, connections):
    
    return {
        "graph": {
            "nodes": make_nodes(node_info),
            "edges": make_edges(disjoint_set, connections),
        }
    }
    
def make_nodes(node_info):

    return {
        node_id: {
            "label": node["name"],
            "metadata": 
                NODE_FORMATTING[node["game"]][node["type"]] 
                | {
                    "click": make_click_html(children_html := make_list_html(sorted(node["child_nodes"]), MARKER_AREA)), 
                    "hover": make_hover_html(children_html)
                }
        }
        for node_id, node in node_info.items()
    }

# AI (chatGPT) wrote most of this function 
# when two nodes have multiple arrows between them, their labels overlay and are essentially unreable.
# The purpose of the complicated bits of this function is to ensure that of all the arrows between two nodes...
# ... only one of them has a label. And that label has to represent the labels of all the other nodes
def make_edges(disjoint_set, connections):
    groups = defaultdict(lambda: {"edges": [], "labels": []})

    for entrance_id, (a, b) in connections.items():
        source = disjoint_set.get_parent(a)
        target = disjoint_set.get_parent(b)
        
        g = groups[frozenset((source, target))]

        g["edges"].append((source, target))
        g["labels"].append(str(entrance_id))

    return [
        {
            "source": source,
            "target": target,
            "metadata": {
                "click": make_click_html(entrances_html := make_list_html(sorted(group["labels"]), MARKER_ENTRANCE)),
                "hover": make_hover_html(entrances_html),
            },
        }
        for group in groups.values()
        for i, (source, target) in enumerate(dict.fromkeys(group["edges"]))
    ]
    
##############################
#### HTML GENERATION #########
##############################

# marker is the character to use as bullet point
def make_list_html(items, marker):
    html = "<" + HTML_LIST_CONTAINER_TAG + " " + HTML_LIST_CONTAINER_ATTRIBUTES.format(marker=marker) + ">"

    for item in items:
        colour = next(HTML_LIST_COLOURS)
        attributes = HTML_LIST_ITEM_ATTRIBUTES.format(cycle_colour=colour)
        html += "<" + HTML_LIST_ITEM_TAG + " " + attributes + ">" + item + "</" + HTML_LIST_ITEM_TAG + ">"

    html += "</" + HTML_LIST_CONTAINER_TAG + ">"

    return html
    
def make_hover_html(text):
    return make_basic_html_container(text, HTML_HOVER_TAG, HTML_HOVER_ATTRIBUTES)

# For text appearing at the bottom of the grapher when something is clicked on
def make_click_html(text):
    return make_basic_html_container(text, HTML_CLICK_TAG, HTML_CLICK_ATTRIBUTES)
    
def make_basic_html_container(text, tag, attributes):
    return "<" + tag + " " + attributes + ">" + text + "</" + tag + ">"
