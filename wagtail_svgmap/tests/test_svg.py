from wagtail_svgmap.svg import find_ids, Link, serialize_svg, SVG_NAMESPACE, wrap_elements_in_links, XLINK_NAMESPACE
from wagtail_svgmap.tests.utils import EXAMPLE_SVG_PATH, IDS_IN_EXAMPLE_SVG


def test_find_ids():
    with open(EXAMPLE_SVG_PATH, 'rb') as infp:
        assert set(find_ids(infp)) == IDS_IN_EXAMPLE_SVG


def test_wrap_elements_in_links():
    with open(EXAMPLE_SVG_PATH, 'rb') as infp:
        tree = wrap_elements_in_links(infp, {
            'green': '/hello',
            'blue': Link('/world', target='_blank'),
        })

    # If wrapping was successful, there should be a couple links whose only child should be green
    id_to_link = {link[0].get('id'): link for link in tree.findall('//{%s}a' % SVG_NAMESPACE)}
    assert id_to_link['green'].get('{%s}href' % XLINK_NAMESPACE) == '/hello'
    assert id_to_link['blue'].get('{%s}target' % SVG_NAMESPACE) == '_blank'
    svg = serialize_svg(tree)
    assert '/hello' in svg
    assert '/world' in svg
    assert '_blank' in svg
