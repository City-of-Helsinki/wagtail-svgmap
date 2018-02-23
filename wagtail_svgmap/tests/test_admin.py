import pytest
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string

from bs4 import BeautifulSoup
from wagtail_svgmap.models import ImageMap
from wagtail_svgmap.tests.utils import IDS_IN_EXAMPLE_SVG
from wsm_test.models import TestPage


@pytest.mark.django_db
def test_admin(admin_client, example_svg_upload):
    admin_client.post(reverse('admin:wagtail_svgmap_imagemap_add'), {
        'title': 'test',
        'svg': example_svg_upload,
    })
    map = ImageMap.objects.get()
    edit_data = {
        '_save': 'Save',
        'title': 'test',
        'regions-TOTAL_FORMS': 2,
        'regions-INITIAL_FORMS': 0,
        'regions-MIN_NUM_FORMS': 0,
        'regions-MAX_NUM_FORMS': 1000,
    }
    for i, data in enumerate([
        {'link_external': 'http://google.com/foo/', 'element_id': 'blue'},
        {'link_external': 'http://google.com/bar/', 'element_id': 'red'},
    ]):
        data.update({'image_map': map.pk, 'id': ''})
        for key, value in data.items():
            edit_data['regions-%d-%s' % (i, key)] = value

    edit_url = reverse('admin:wagtail_svgmap_imagemap_change', args=(map.pk,))

    # Check that the select boxes get populated with the element IDs
    response = admin_client.get(edit_url, edit_data)
    response.render()
    content = response.content.decode('utf-8')
    for id in IDS_IN_EXAMPLE_SVG:
        assert id in content

    # Now do some editing!
    admin_client.post(edit_url, edit_data)
    map = ImageMap.objects.get()
    assert map.regions.count() == 2
    assert '/foo/' in map.rendered_svg
    assert '/bar/' in map.rendered_svg


@pytest.mark.django_db
def test_page_creation(admin_client, root_page, example_imagemap):
    """
    A test for issue #9 (i.e. that admin views for pages with streamblocks
    with imagemapfields do retain their choice when the page is opened).
    """
    # First, create the page using the admin:
    title = get_random_string(allowed_chars='oeiu')
    admin_client.post(
        reverse(
            'wagtailadmin_pages:add',
            args=('wsm_test', 'testpage', root_page.pk,),
        ),
        {
            'next': '',
            'title': title,
            'body-count': '1',
            'body-0-deleted': '',
            'body-0-order': '0',
            'body-0-type': 'imagemap',
            'body-0-value-map': example_imagemap.pk,
            'body-0-value-css_class': 'erd',
            'slug': title,
            'seo_title': '',
            'search_description': '',
            'go_live_at': '',
            'expire_at': '',
        }
    )
    # Retrieve it...
    page = TestPage.objects.get(slug=title)

    # Go to the edit page...
    content = admin_client.get(reverse('wagtailadmin_pages:edit', args=(page.pk,))).content
    # ... and check that the imagemap streamblock has the correct option selected:
    select = BeautifulSoup(content, 'html.parser').find(id='body-0-value-map')
    example_map_option = select.find(value=str(example_imagemap.pk))
    assert example_map_option.get('selected') is not None