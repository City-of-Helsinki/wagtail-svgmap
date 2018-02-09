from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.forms import Select
from django.forms.utils import flatatt
from django.utils.html import escape, mark_safe
from django.utils.translation import ugettext_lazy as _

try:
    from wagtail.core import blocks
except ImportError:
    from wagtail.wagtailcore import blocks

from wagtail_svgmap.models import ImageMap


class _ImageMapChoiceBlock(blocks.ChooserBlock):
    """
    Internal choice block; you shouldn't need to worry about this.
    """

    target_model = ImageMap
    widget = Select

    def value_for_form(self, value):
        if hasattr(value, 'pk'):
            return value.pk
        return value

    def value_from_form(self, value):
        return super(_ImageMapChoiceBlock, self).value_from_form(value or None)


class ImageMapBlock(blocks.StructBlock):
    """
    A StructBlock for StreamFields for choosing an ImageMap object and wrapping it in a CSS class.
    """

    map = _ImageMapChoiceBlock(required=True, label=_('Image map'))
    css_class = blocks.CharBlock(required=False, label=_('CSS class'))

    # Feel free to override this in an `ImageMapBlock` subclass of your own!
    ie_compatibility = getattr(settings, 'WAGTAIL_SVGMAP_IE_COMPAT', True)

    def render(self, value, context=None):
        if not value:  # pragma: no cover
            return ''

        image_map = value['map']
        if not image_map:  # pragma: no cover
            return ''
        assert isinstance(image_map, ImageMap)

        attrs = self.get_container_attrs(value)
        assert 'id' in attrs  # required for the inline style

        wrapper = '<div%(attrs)s>%(svg)s</div>' % {
            'attrs': flatatt({k: v for (k, v) in attrs.items() if (k and v)}),
            'svg': image_map.rendered_svg,
        }

        if self.ie_compatibility:  # pragma: no branch
            wrapper += '<style>%(style)s</style>' % {
                'style': '#%s svg{position:absolute;top:0;left:0}' % attrs['id'],
            }

        return mark_safe(wrapper)

    def compute_wrapper_style(self, image_map):
        if not self.ie_compatibility:  # pragma: no cover
            return None
        # * See http://tympanus.net/codrops/2014/08/19/making-svgs-responsive-with-css/
        #   for the source of this sorcery.

        try:
            height, width = image_map.size
            aspect_ratio = (height / width)
        except ZeroDivisionError:  # pragma: no cover
            # Assume square, that's about the best we can do
            aspect_ratio = 1

        width = 100  # left as a variable for future expansion
        style = ';'.join([
            'height: 0',  # collapse the container's height
            'width: %s%%' % width,  # specify any width you want (a percentage value, basically)
            'padding-top: %s%%' % (width / aspect_ratio),  # makes sure the AR of the container equals the svg's
            'position: relative',  # create positioning context for svg
        ]).replace(' ', '')
        return style

    def get_container_attrs(self, value):
        image_map = value['map']
        style = self.compute_wrapper_style(image_map)

        return {
            'id': ('image-map-%s' % image_map.pk),
            'class': escape(value['css_class'] or ''),
            'style': style,
        }

    class Meta:
        icon = "image"
