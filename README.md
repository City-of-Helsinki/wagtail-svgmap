# wagtail-svgmap

> Image map functionality for Wagtail through inline SVGs

## Usage

### As a developer

* Add `wagtail_svgmap` to your `INSTALLED_APPS`
* Add a `wagtail_svgmap.blocks.ImageMapBlock()` to a `StreamField` in your page class

### As an end user

#### Using the Wagtail Admin

* If `wagtail.contrib.modeladmin` is enabled, `ImageMap` objects can be created
  from the Wagtail admin (look for "Image Maps" in the menu).
  Once you've selected an SVG file, you can create region objects to set which
  pages/documents/external URLs each discovered ID should link to.

#### Using the Django Admin

* Use the Django admin interface to create `ImageMap` objects.
  Once you've selected an SVG file, you can then set which pages/documents/external URLs
  each discovered ID should link to.

#### In pages

* In a page that has an `ImageMapBlock`-enabled stream field, select the image map to use.
  You can also additionally set a CSS class to wrap the field with. Ask your friendly
  neighborhood designer for more information.

## Development

* Use `py.test` for testing.
