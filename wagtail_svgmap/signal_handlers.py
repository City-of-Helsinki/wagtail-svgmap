from wagtail.wagtailcore.models import Page
from wagtail.wagtaildocs.models import Document
from wagtail_svgmap import log
from wagtail_svgmap.models import ImageMap


def handle_recache_imagemap(instance, **kwargs):
    """
    Django `post_save` handler to automatically recache the rendered SVG for
    ImageMap instances when dependencies (pages and documents) change.

    :param instance: The changed instance (either a Page or Document)
    :param kwargs: Signal kwargs
    """
    if isinstance(instance, Page):  # pragma: no branch
        linked_maps = ImageMap.objects.filter(regions__link_page=instance)
    elif isinstance(instance, Document):  # pragma: no branch
        linked_maps = ImageMap.objects.filter(regions__link_document=instance)
    else:  # pragma: no cover
        linked_maps = []

    for map in linked_maps:
        map.recache_svg(save=True)
        log.info('Recached image map %s because %s changed', map.pk, instance)
