# wagtail-svgmap

> Image map functionality for Wagtail through inline SVGs

## Usage

### As a developer

* Add `wagtail_svgmap` to your `INSTALLED_APPS`
* Add a `wagtail_svgmap.blocks.ImageMapBlock()` to a `StreamField` in your page class

#### Settings

* `WAGTAIL_SVGMAP_IE_COMPAT`: Whether or not to wrap the rendered SVGs in special markup
                              for compatibility with legacy Internet Explorers.  Enabled
                              by default; disabling leads to slightly nicer markup.

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

#### In the Wagtail Admin

* In a page that has an `ImageMapBlock`-enabled stream field, select the image map to use.
  You can also additionally set a CSS class to wrap the field with. Ask your friendly
  neighborhood designer for more information.

### Rendering in Templates

* Blocks of type `ImageMapBlock` usually render in the StreamField.
  Some uses of include can stop StreamField elements like `ImageMapBlock` from rendering.
  You can render the svg map manually by calling `map.rendered_svg` on the block
  in your template: `block_with_imagemap.map.rendered_svg|safe`

## Development

* Use `py.test` for testing.
