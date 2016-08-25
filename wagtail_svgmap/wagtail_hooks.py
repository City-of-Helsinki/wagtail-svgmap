from django.conf import settings

if 'wagtail.contrib.modeladmin' in settings.INSTALLED_APPS:  # pragma: no cover
    import wagtail_svgmap.modeladmin as ma
    ma.register()
