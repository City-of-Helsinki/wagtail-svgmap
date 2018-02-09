# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
try:
    from wagtail.core.models import Page
except ImportError:
    from wagtail.wagtailcore.models import Page


def create_homepage(apps, schema_editor):
    ContentType = apps.get_model('contenttypes.ContentType')
    Site = apps.get_model('wagtailcore.Site')
    TestPage = apps.get_model('wsm_test.TestPage')
    Page.objects.get(id=2).delete()  # delete default page
    homepage = TestPage(title='Page', slug='home', content_type=ContentType.objects.get_for_model(TestPage))
    root = Page.objects.get(slug='root')
    root.numchild = len(root.get_children())  # Recalculate the root's child count, just in case
    root.add_child(instance=homepage)
    Site.objects.create(hostname='localhost', root_page=homepage, is_default_site=True)
    ContentType.objects._cache.clear()


class Migration(migrations.Migration):
    dependencies = [
        ('wsm_test', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_homepage),
    ]
