import pytest
from django.core.urlresolvers import reverse

from wagtail_svgmap.models import ImageMap
from wagtail_svgmap.tests.utils import IDS_IN_EXAMPLE_SVG


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
