from operator import attrgetter

from django.shortcuts import redirect
from django.utils.http import urlencode

try:
    from wagtail.contrib.modeladmin.options import ModelAdmin
    from wagtail.contrib.modeladmin.views import CreateView, EditView
    from wagtail.admin import messages
except ImportError:
    from wagtail.contrib.modeladmin.options import ModelAdmin
    from wagtail.contrib.modeladmin.views import CreateView, EditView
    from wagtail.wagtailadmin import messages
from wagtail_svgmap.models import ImageMap, Region


class ImageMapEditView(EditView):
    def get_context_data(self, **kwargs):
        context = super(ImageMapEditView, self).get_context_data(**kwargs)
        context['regions'] = self.get_edit_regions()
        return context

    def get_edit_regions(self):
        assert isinstance(self.instance, ImageMap)
        regions = {region.element_id: region for region in self.instance.regions.all()}
        element_ids = self.instance.ids
        for element_id in element_ids:
            if element_id not in regions:
                regions[element_id] = Region(image_map=self.instance, element_id=element_id)
        regions = sorted(regions.values(), key=attrgetter('element_id'))
        from .regions import RegionModelAdmin
        region_url_helper = RegionModelAdmin().url_helper
        for region in regions:
            if region.pk:
                region.edit_url = region_url_helper.get_action_url('edit', region.pk)
            else:
                region.edit_url = '%s?%s' % (
                    region_url_helper.create_url,
                    urlencode({
                        'image_map': self.instance.pk,
                        'element_id': region.element_id,
                    })
                )
        return regions


class ImageMapCreateView(CreateView):
    def get_success_url(self):
        return self.url_helper.get_action_url('edit', self.instance.pk)

    def form_valid(self, form):
        self.instance = instance = form.save()
        messages.success(
            self.request,
            self.get_success_message(instance),
            buttons=self.get_success_message_buttons(instance)
        )
        return redirect(self.get_success_url())


class ImageMapModelAdmin(ModelAdmin):
    model = ImageMap
    menu_icon = 'image'
    list_display = ('title',)
    search_fields = ('title',)
    edit_template_name = 'wagtail_svgmap/modeladmin/edit_imagemap.html'
    edit_view_class = ImageMapEditView
    create_view_class = ImageMapCreateView
