import os

EXAMPLE_SVG_PATH = os.path.join(os.path.dirname(__file__), 'example.svg')
IDS_IN_EXAMPLE_SVG = {'red', 'yellow', 'blue', 'green'}
IDS_IN_EXAMPLE2_SVG = {'punainen', 'keltainen', 'sininen', 'vihrea'}

with open(EXAMPLE_SVG_PATH, 'rb') as infp:
    EXAMPLE_SVG_DATA = infp.read()

EXAMPLE2_SVG_DATA = (
    EXAMPLE_SVG_DATA
    .replace(b'"red"', b'"punainen"')
    .replace(b'"green"', b'"vihrea"')
    .replace(b'"blue"', b'"sininen"')
    .replace(b'"yellow"', b'"keltainen"')
)
