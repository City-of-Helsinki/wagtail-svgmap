from django.db import models
from django.utils.translation import ugettext_lazy as _

try:
    from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
    from wagtail.documents.edit_handlers import DocumentChooserPanel
except ImportError:
    from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel
    from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel


class LinkFields(models.Model):
    # h/t https://github.com/torchbox/wagtaildemo/blob/e73170a1ac4eb30f1a071e81542b21c136ced1cd/demo/models.py#L85
    link_external = models.URLField(
        verbose_name=_('external link'),
        blank=True
    )
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_('linked page'),
        on_delete=models.CASCADE,
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_('linked document'),
        on_delete=models.CASCADE,
    )

    @property
    def link(self):
        """
        Get the actual link URL for this object.

        :return: URL string (might be empty)
        :rtype: str
        """
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True
