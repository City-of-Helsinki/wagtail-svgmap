import os

EXAMPLE_SVG_PATH = os.path.join(os.path.dirname(__file__), 'example.svg')
IDS_IN_EXAMPLE_SVG = {'red', 'yellow', 'blue', 'green'}

with open(EXAMPLE_SVG_PATH, 'rb') as infp:
    EXAMPLE_SVG_DATA = infp.read()
