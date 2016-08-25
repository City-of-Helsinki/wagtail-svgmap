from wagtail.contrib.modeladmin.options import modeladmin_register

from .image_maps import ImageMapModelAdmin
from .regions import RegionModelAdmin


def register():
    modeladmin_register(ImageMapModelAdmin)
    modeladmin_register(RegionModelAdmin)
