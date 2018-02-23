from django.forms.widgets import HiddenInput, Select
from django.shortcuts import redirect

from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView, DeleteView, EditView
try:
    from wagtail.admin import messages
except ImportError:
    from wagtail.wagtailadmin import messages
from wagtail_svgmap.models import ImageMap, Region

from .image_maps import ImageMapModelAdmin


class RegionCommonMixin(object):
    def get_initial(self):
        initial = super(RegionCommonMixin, self).get_initial()
        initial.update(dict(self.request.GET.items()))
        return initial

    def get_success_url(self):
        return ImageMapModelAdmin().url_helper.get_action_url('edit', self.instance.image_map_id)

    def get_context_data(self, **kwargs):
        context = super(RegionCommonMixin, self).get_context_data(**kwargs)
        image_map = None
        region = getattr(self, 'instance', Region())
        if region.pk:
            image_map = region.image_map
        else:
            try:
                image_map = ImageMap.objects.get(pk=self.request.GET['image_map'])
            except:  # pragma: no cover
                # the image map parameter could be incorrect (if manually entered); ah well
                pass

        if image_map and 'form' in context:  # pragma: no branch
            # Switch the element ID widget to a select, since we can't have
            # a ChoiceField of element IDs.
            context['form'].fields['element_id'].widget = Select(
                choices=[(id, id) for id in image_map.ids]
            )
            # Hide the image map widget (unfortunately the group header remains).
            context['form'].fields['image_map'].widget = HiddenInput()

        context['image_map'] = image_map

        return context


class RegionEditView(RegionCommonMixin, EditView):
    pass


class RegionCreateView(RegionCommonMixin, CreateView):
    def form_valid(self, form):
        # Need to assign `self.instance` to make `RegionCommonMixin` work.
        self.instance = instance = form.save()
        messages.success(
            self.request, self.get_success_message(instance),
            buttons=self.get_success_message_buttons(instance),
        )
        return redirect(self.get_success_url())


class RegionDeleteView(RegionCommonMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        # This seems to be the least intrusive way to redirect back to the imagemap
        self.index_url = self.get_success_url()
        return super(RegionDeleteView, self).post(request, *args, **kwargs)


class RegionModelAdmin(ModelAdmin):
    model = Region
    menu_icon = 'image'
    create_view_class = RegionCreateView
    edit_view_class = RegionEditView
    delete_view_class = RegionDeleteView
    edit_template_name = 'wagtail_svgmap/modeladmin/edit_region.html'
    create_template_name = 'wagtail_svgmap/modeladmin/edit_region.html'
