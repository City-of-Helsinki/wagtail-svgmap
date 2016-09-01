import pytest
from django.core.files.base import ContentFile

from wagtail.wagtailcore.models import Page
from wagtail_svgmap.models import ImageMap
from wagtail_svgmap.tests.utils import EXAMPLE2_SVG_DATA, IDS_IN_EXAMPLE2_SVG, IDS_IN_EXAMPLE_SVG


@pytest.mark.django_db
def test_id_caching(example_svg_upload):
    map = ImageMap.objects.create(svg=example_svg_upload)
    assert map.ids == IDS_IN_EXAMPLE_SVG
    assert map.size == (588, 588)


@pytest.mark.django_db
def test_image_replacing(example_svg_upload):
    map = ImageMap.objects.create(svg=example_svg_upload)
    assert map.ids == IDS_IN_EXAMPLE_SVG
    map.svg.save('example2.svg', ContentFile(EXAMPLE2_SVG_DATA))
    map.save()
    map.refresh_from_db()
    assert map.ids == IDS_IN_EXAMPLE2_SVG


@pytest.mark.django_db
def test_rendering(root_page, example_svg_upload, dummy_wagtail_doc):
    page = Page(title="nnep", slug="nnep")
    page.set_url_path(root_page)
    root_page.add_child(instance=page)
    page.save()
    assert page.url

    map = ImageMap.objects.create(svg=example_svg_upload)
    map.regions.create(element_id='green', link_external='/foobar', target='_blank')
    map.regions.create(element_id='blue', link_page=page, target='_top')
    map.regions.create(element_id='red', link_document=dummy_wagtail_doc)

    svg = map.rendered_svg
    assert '/foobar' in svg
    assert '_blank' in svg
    assert 'nnep' in svg
    assert '_top' in svg
    assert ('documents/%s' % dummy_wagtail_doc.pk) in svg


@pytest.mark.django_db
def test_auto_recache(root_page, example_svg_upload):
    page = Page(title="nnep", slug="nnep")
    page.set_url_path(root_page)
    root_page.add_child(instance=page)
    page.save()
    assert page.url

    map = ImageMap.objects.create(svg=example_svg_upload)
    map.regions.create(element_id='blue', link_page=page)
    map.recache_svg(save=True)
    assert 'nnep' in map.rendered_svg
    page.slug = 'ffflop'
    page.save()  # The `post_save` triggers will get called...
    assert 'ffflop' in ImageMap.objects.get(pk=map.pk).rendered_svg
