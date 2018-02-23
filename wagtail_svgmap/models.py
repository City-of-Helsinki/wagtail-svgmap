from __future__ import unicode_literals

from contextlib import closing

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

try:
    from wagtail.admin.edit_handlers import FieldPanel
except ImportError:
    from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail_svgmap import log
from wagtail_svgmap.mixins import LinkFields
from wagtail_svgmap.svg import find_ids, fix_dimensions, get_dimensions, Link, serialize_svg, wrap_elements_in_links


@python_2_unicode_compatible
class ImageMap(models.Model):
    """
    The main image map model. Caches the element IDs and prerendered linked SVG.
    """

    title = models.CharField(max_length=255, verbose_name=_('title'))
    svg = models.FileField(
        upload_to='imagemaps/%Y/%m/%d',
        verbose_name=_('SVG file'),
        help_text=_('Choose a valid SVG file. The document must contain elements that have IDs.'),
    )
    _ids_cache = models.TextField(editable=False, blank=True, db_column='ids_cache')
    _render_cache = models.TextField(editable=False, blank=True, db_column='render_cache')
    _width_cache = models.FloatField(editable=False, default=0, db_column='width_cache')
    _height_cache = models.FloatField(editable=False, default=0, db_column='height_cache')

    @property
    def rendered_svg(self):
        """
        Get the rendered (linkified) SVG markup.

        If for some reason the render cache is empty,
        this will always rerender the markup.

        :return: string of XML
        :rtype: str
        """
        if not self._render_cache:  # pragma: no cover
            self.recache_svg()
        return self._render_cache

    @property
    def original_svg(self):
        """
        Get the original SVG markup from the `svg` file.

        :return: string of XML
        :rtype: str
        """
        with self._open_original() as infp:
            return infp.read()

    @property
    def ids(self):
        """
        Get a set of element IDs discovered in the SVG file.

        If for some reason the ID cache is empty,
        it will always be recached here.

        :return: set of ID strings (without leading octothorpes)
        :rtype: set[str]
        """
        if not self._ids_cache:  # pragma: no cover
            self.recache_ids()
        return set(self._ids_cache.splitlines() if self._ids_cache else ())

    @property
    def size(self):
        """
        Get the dimensions of the rendered SVG.

        If one or more dimensions are invalid, the (0, 0) tuple is returned.

        :return: Width/height tuple
        :rtype: tuple[float, float]
        """
        return (self._width_cache, self._height_cache)

    def save(self, *args, **kwargs):
        super(ImageMap, self).save(*args, **kwargs)
        if self.recache_ids() | self.recache_svg():  # Using `|` for non-short-circuited or
            self.save()

    def recache_ids(self, save=False):
        """
        Refresh the ID cache.

        :param save: Save the ID cache to the database while at it?
        :type save: bool
        :return: True if the cache changed.
        :rtype: bool
        """
        old_ids_cache = self._ids_cache
        with self._open_original() as stream:
            self._ids_cache = '\n'.join(sorted(set(find_ids(stream))))
        changed = (self._ids_cache != old_ids_cache)
        if changed and save:  # pragma: no cover
            models.Model.save(self, update_fields=('_ids_cache',))
        return changed

    def recache_svg(self, save=False):
        """
        Refresh the rendered SVG cache.

        :param save: Save the SVG cache to the database while at it?
        :type save: bool
        :return: True if the cache changed.
        :rtype: bool
        """
        old_values = (self._render_cache, self._width_cache, self._height_cache)
        new_values = self._render()
        changed = (old_values != new_values)
        (self._render_cache, self._width_cache, self._height_cache) = new_values
        if changed and save:
            models.Model.save(self, update_fields=(
                '_render_cache',
                '_width_cache',
                '_height_cache',
            ))
        return changed

    def _open_original(self):
        stream = self.svg
        stream.open()
        if stream.tell():  # pragma: no cover
            stream.seek(0)
        return closing(stream)

    def _render(self):
        links = {
            region.element_id: Link(url=region.link, target=region.target)
            for region
            in self.regions.select_related('link_page', 'link_document').all()
        }
        with self._open_original() as stream:
            tree = wrap_elements_in_links(stream, links)
            fix_dimensions(tree)

        try:
            width, height = get_dimensions(tree)
        except:  # pragma: no cover
            log.warn('unable to determine dimensions for %s' % self.pk, exc_info=True)
            width = height = 0

        rendered = serialize_svg(tree, xml_declaration=False)
        for element_id, link in links.items():  # Sanity check
            if element_id in rendered:  # If the target element exists at all,
                assert link.url in rendered  # The link URL should be there too
        return (rendered, width, height)

    def __str__(self):  # pragma: no cover
        return self.title


@python_2_unicode_compatible
class Region(LinkFields, models.Model):
    """
    Child model to specify the link target for a given element in a given image map.
    """

    image_map = models.ForeignKey(to=ImageMap, related_name='regions', on_delete=models.SET_NULL)
    element_id = models.CharField(verbose_name=_('element ID'), max_length=64)
    target = models.CharField(
        verbose_name=_('link target'), blank=True, max_length=64,
        help_text=_('Use _blank to open links in new windows.')
    )

    class Meta:
        unique_together = [
            ('image_map', 'element_id'),
        ]

    def __str__(self):  # pragma: no cover
        text = '#%s' % self.element_id
        if self.link:
            text += '\u2192 %s' % self.link
        return text

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Region, self).save(force_insert, force_update, using, update_fields)
        self.image_map.recache_svg(save=True)

    panels = [
        FieldPanel('image_map'),
        FieldPanel('element_id'),
        FieldPanel('target'),
    ] + LinkFields.panels
