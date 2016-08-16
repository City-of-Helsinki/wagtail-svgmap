from django.apps import AppConfig
from django.db.models.signals import post_save


class WagtailSvgmapConfig(AppConfig):
    name = 'wagtail_svgmap'
    verbose_name = 'Wagtail-Svgmap'

    def ready(self):
        from .signal_handlers import handle_recache_imagemap
        post_save.connect(handle_recache_imagemap, sender='wagtailcore.Page')
        post_save.connect(handle_recache_imagemap, sender='wagtaildocs.Document')
