from django import forms
from django.contrib import admin

from wagtail_svgmap.models import ImageMap, Region


class RegionInline(admin.TabularInline):
    model = Region
    raw_id_fields = ('link_page', 'link_document',)

    def get_formset(self, request, obj=None, **kwargs):
        # Fix up the region formsets to have valid ID choices...
        id_choices = [('', '---------')] + [(id, id) for id in sorted(getattr(obj, 'ids', ()))]

        def formfield_callback(db_field):
            field = self.formfield_for_dbfield(db_field, request=request)
            if db_field.name == 'element_id':
                field = forms.ChoiceField(
                    choices=id_choices,
                    label=field.label,
                    help_text=field.help_text,
                )
            return field

        kwargs['formfield_callback'] = formfield_callback
        return super(RegionInline, self).get_formset(request, obj, **kwargs)


class ImageMapAdmin(admin.ModelAdmin):
    inlines = [RegionInline]

    def get_inline_instances(self, request, obj=None):
        if not getattr(obj, 'svg', None):  # No SVG selected? Pff.
            return []
        return super(ImageMapAdmin, self).get_inline_instances(request, obj=obj)

    def save_related(self, request, form, formsets, change):
        super(ImageMapAdmin, self).save_related(request, form, formsets, change)
        # After the inlines have been saved, let's recache the rendered SVG
        assert isinstance(form.instance, ImageMap)
        form.instance.recache_svg(save=True)


admin.site.register(ImageMap, ImageMapAdmin)
