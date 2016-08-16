from __future__ import unicode_literals

from contextlib import closing

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from wagtail_svgmap.mixins import LinkFields
from wagtail_svgmap.svg import find_ids, Link, serialize_svg, wrap_elements_in_links


@python_2_unicode_compatible
class ImageMap(models.Model):
    svg = models.ForeignKey(
        to='wagtaildocs.Document',
        on_delete=models.PROTECT,
        verbose_name=_('SVG document'),
        help_text=_('Choose a valid SVG document. The document must contain elements that have IDs.'),
    )
    _ids_cache = models.TextField(editable=False, blank=True, db_column='ids_cache')
    _render_cache = models.TextField(editable=False, blank=True, db_column='render_cache')

    @property
    def rendered_svg(self):
        if not self._render_cache:
            self.recache_svg()
        return self._render_cache

    @property
    def ids(self):
        if not self._ids_cache:  # pragma: no cover
            self.recache_ids()
        return set(self._ids_cache.splitlines() if self._ids_cache else ())

    def clean(self):
        if self.svg_id:  # pragma: no branch
            self.recache_ids()
            if not self.ids:  # pragma: no cover
                raise ValidationError('The selected SVG file (%s) contains no IDs' % self.svg.filename)
        if self.pk and self.svg_id:
            self.recache_svg()

    def save(self, *args, **kwargs):
        self.clean()
        super(ImageMap, self).save(*args, **kwargs)

    def recache_ids(self, save=False):
        with self._open_original() as stream:
            self._ids_cache = '\n'.join(sorted(set(find_ids(stream))))
            if save:  # pragma: no cover
                models.Model.save(self, update_fields=('_ids_cache',))

    def recache_svg(self, save=False):
        self._render_cache = self._render()
        if save:
            models.Model.save(self, update_fields=('_render_cache',))

    def _open_original(self):
        stream = self.svg.file
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
        rendered = serialize_svg(tree, xml_declaration=False)
        for link in links.values():  # Sanity check
            assert link.url in rendered
        return rendered

    def __str__(self):  # pragma: no cover
        return self.svg.title


@python_2_unicode_compatible
class Region(LinkFields, models.Model):
    image_map = models.ForeignKey(to=ImageMap, related_name='regions')
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
        return '#%s \u2192 %s' % (self.element_id, self.link)
