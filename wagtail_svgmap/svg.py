import re

from six import BytesIO

try:  # pragma: no cover
    from xml.etree import cElementTree as ET
except ImportError:  # pragma: no cover
    from xml.etree import ElementTree as ET

SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'

ET.register_namespace('svg', SVG_NAMESPACE)
ET.register_namespace('xlink', XLINK_NAMESPACE)

VISIBLE_SVG_TAGS = frozenset({
    # See https://developer.mozilla.org/en-US/docs/Web/SVG/Element
    'a',
    'circle',
    'ellipse',
    'g',
    'image',
    'line',
    'path',
    'polygon',
    'polyline',
    'rect',
    'switch',
    'text',
    'textPath',
    'tref',
    'tspan',
    'use',
})


def find_ids(svg_stream, in_elements=VISIBLE_SVG_TAGS):
    """
    Find element IDs in a stream (file-like) of SVG data.

    :param svg_stream: The SVG stream to parse.
    :param in_elements: Set of namespace-agnostic element names to consider.
    :return: Iterator of ids; uniqueness not guaranteed.
    :rtype: Iterator[str]
    """
    for event, elem in ET.iterparse(svg_stream, events=('end',)):
        tag_without_ns = elem.tag.split('}')[-1]
        if in_elements and tag_without_ns not in in_elements:
            continue
        id = elem.get('id')
        if id:  # pragma: no branch
            yield id


class Link(object):
    """
    Wrapper object for link specification.
    """

    def __init__(self, url, target=None):
        """
        Construct a link.

        :param url: The URL to link to.
        :type url: str
        :param target: Optional link target (HTML semantics; `_blank` for a new window, etc.)
        :type target: str|None
        """
        self.url = str(url)
        self.target = target

    def get_element(self):
        """
        Render the link as an SVG `<a>` element.

        :rtype: xml.etree.ElementTree.Element
        """
        return ET.Element(
            '{%s}a' % SVG_NAMESPACE,
            dict(kv for kv in self.get_element_attribs().items() if kv[0] and kv[1])
        )

    def get_element_attribs(self):
        """
        Get a dictionary of attributes for the element.

        This could be niftily replaced in subclasses.

        :return: key-value dict
        :rtype: dict[str, str]
        """
        return {
            ('{%s}href' % XLINK_NAMESPACE): self.url,
            ('{%s}target' % SVG_NAMESPACE): self.target,
        }


def wrap_elements_in_links(tree, id_to_url_map, in_elements=VISIBLE_SVG_TAGS):
    """
    Wrap elements in `<a>` elements in the tree according to the given `id_to_url_map`.

    :param tree: The tree to process. May be an `ElementTree` object, or a filename, or a SVG stream.
                 If a tree is passed in, it will be modified in-place.
    :type tree: xml.etree.ElementTree.ElementTree|str|file
    :param id_to_url_map: A mapping from element IDs to URLs.
                          Here `URL` may either be a string or a `Link` instance; using `Link`s
                          makes it possible to set link `target`s among other things.
    :param in_elements: Set of namespace-agnostic element names to consider.
    :return: A modified ElementTree tree.
    :rtype: xml.etree.ElementTree.ElementTree
    """
    if isinstance(tree, str) or hasattr(tree, 'read'):  # pragma: no branch
        tree = ET.parse(tree)
    # h/t http://stackoverflow.com/a/20132342/51685
    parent_map = {child: parent for parent in tree.iter() for child in parent}

    # First, find the elements that we are interested in wrapping:
    element_to_url = {}
    for elem in parent_map.keys():
        tag_without_ns = elem.tag.split('}')[-1]
        if in_elements and tag_without_ns not in in_elements:
            continue
        url = id_to_url_map.get(elem.get('id'))
        if not url:
            continue

        if isinstance(url, str):
            url = Link(url)
        element_to_url[elem] = url

    # Then wrap them!

    for elem, url in element_to_url.items():
        a_element = url.get_element()
        parent = parent_map[elem]

        # Find the original insertion position
        for index, test_element in enumerate(parent):
            if elem is test_element:
                break
        else:  # pragma: no cover
            raise ValueError("tree broken")
        parent.remove(elem)  # Remove the unwrapped node from the parent
        a_element.append(elem)  # Wrap the node in the A element
        elem.tail = (elem.tail or '').strip()  # Remove any trailing spaces from the wrapped element
        parent.insert(index, a_element)  # Replace the wrapped node into the parent
        parent_map[elem] = a_element  # Update the parent map
    return tree


def fixup_unqualified_attributes(tree, namespace):
    """
    Fix unqualified attributes in the `tree` to be `namespace` prefixed.

    :param tree: The tree to process.
    :type tree: xml.etree.ElementTree.ElementTree
    :param namespace: The namespace (sans braces) to add.
    :type namespace: str
    :return: The processed tree, modified in-place
    :rtype: xml.etree.ElementTree.ElementTree
    """
    for elem in tree.iter():
        for key in [key for key in elem.keys() if key[0] != '{']:
            elem.attrib['{%s}%s' % (namespace, key)] = elem.attrib.pop(key)
    return tree


def serialize_svg(tree, encoding='UTF-8', xml_declaration=True):
    """
    Serialize an ElementTree as SVG.

    :param tree: The tree to process.
    :type tree: xml.etree.ElementTree.ElementTree
    :param xml_declaration: Whether to emit the XML declaration tag or not
    :type xml_declaration: bool
    :return: the serialized XML (as an Unicode string)
    :rtype: str
    """
    bio = BytesIO()
    fixup_unqualified_attributes(tree, namespace=SVG_NAMESPACE)
    tree.write(bio, encoding=encoding, xml_declaration=xml_declaration, default_namespace=SVG_NAMESPACE)
    return bio.getvalue().decode(encoding)


def fix_dimensions(tree):
    """
    "Fix" the dimension attributes of the SVG in-place.

    Basically, this replaces hard-coded width and height with a viewbox.

    :param tree: The tree to process.
    :type tree: xml.etree.ElementTree.ElementTree
    :return: None; the tree is (possibly) modified in-place.
    """
    root = tree.getroot()
    assert root.tag.endswith('svg')
    if 'viewBox' not in root.attrib:
        # Try to generate a viewbox if possible
        width = root.attrib.get('width')
        height = root.attrib.get('height')
        if width and height:
            root.attrib['viewBox'] = '0 0 %s %s' % (width, height)
        else:
            return
    root.attrib.pop('width', None)
    root.attrib.pop('height', None)


def get_dimensions(tree):
    """
    Get the declared dimensions of an SVG tree.


    :param tree: The tree to process.
    :type tree: xml.etree.ElementTree.ElementTree
    :return: Dimensions (2-tuple of floats) or None if unknown.
    :rtype: tuple[float, float]|None
    """
    root = tree.getroot()
    assert root.tag.endswith('svg')
    if 'viewBox' in root.attrib:
        # Use viewbox ("min-x, min-y, width, height"), separated by whitespace and/or a comma
        viewbox = re.split(r'[, ]+', root.attrib['viewBox'])
        return (float(viewbox[2]), float(viewbox[3]))
    else:
        # Use width/height
        width = root.attrib.get('width')
        height = root.attrib.get('height')
        if width and height:
            return (float(width), float(height))
