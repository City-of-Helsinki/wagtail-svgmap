import pytest
from wagtail_svgmap.modeladmin import ImageMapModelAdmin
from wagtail_svgmap.modeladmin.regions import RegionModelAdmin
from wagtail_svgmap.models import ImageMap, Region
from wagtail_svgmap.tests.utils import IDS_IN_EXAMPLE_SVG


@pytest.mark.django_db
def test_modeladmin(admin_client, example_svg_upload):
    region_url_helper = RegionModelAdmin().url_helper
    resp = admin_client.post(ImageMapModelAdmin().url_helper.create_url, {
        'title': 'test',
        'svg': example_svg_upload,
    }, follow=True)

    # Test that the links to creating regions work:
    resp.render()
    content = resp.content.decode('utf8')
    for id in IDS_IN_EXAMPLE_SVG:
        assert 'element_id=%s' % id in content

    map = ImageMap.objects.get(title='test')
    admin_client.get('%s?image_map=%d&element_id=blue' % (region_url_helper.create_url, map.pk))
    admin_client.post(region_url_helper.create_url, {
        'image_map': map.pk,
        'element_id': 'blue',
        'link_external': 'http://google.com/foo/',
    })
    map = ImageMap.objects.get()
    assert map.regions.count() == 1
    region = map.regions.get(element_id='blue')
    assert '/foo/' in map.rendered_svg

    # And then delete that region
    delete_region_url = region_url_helper.get_action_url('delete', region.pk)
    admin_client.get(delete_region_url)
    admin_client.post(delete_region_url)
    assert not Region.objects.filter(image_map=map, element_id='blue').exists()
