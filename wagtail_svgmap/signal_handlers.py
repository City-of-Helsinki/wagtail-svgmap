try:
    from wagtail.core.models import Page
    from wagtail.documents.models import Document
except ImportError:
    from wagtail.wagtailcore.models import Page
    from wagtail.wagtaildocs.models import Document

from wagtail_svgmap import log
from wagtail_svgmap.models import ImageMap


def handle_recache_imagemap(instance, **kwargs):
    """
    Django `post_save` handler to automatically recache rendered SVGs.

    This is called for ImageMap instances when region link
    dependencies (pages and documents) change.

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
        if map.recache_svg(save=True):  # pragma: no branch
            log.info('Recached image map %s because %s changed', map.pk, instance)
