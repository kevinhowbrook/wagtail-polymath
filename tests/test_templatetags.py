from django.test import TestCase, override_settings

from wagtail_polymath.config import ENGINES
from wagtail_polymath.templatetags.wagtail_polymath import (
    _build_attributes,
    polymath_scripts,
    polymath_stylesheets,
)


CUSTOM_JS_URL = "https://example.com/mathjax/tex-mml-chtml.js"
CUSTOM_SRI = "sha256-Ynv3Q3nAtRTr6UDX+X6vbn9d1t8ZO5oV2Y4gvL9y0ck="


class TestScriptsTemplateTag(TestCase):
    def test_template_tag_uses_default_url_and_integrity(self):
        default_url = ENGINES["mathjax"]["libraries"][0]["url"]
        default_sri = ENGINES["mathjax"]["libraries"][0]["sri"]

        html = polymath_scripts()
        self.assertInHTML(
            f'<script src="{default_url}" integrity="{default_sri}" crossorigin="anonymous" defer></script>',
            html,
        )
        self.assertIn("wagtail_polymath/js/mathjax_init.js", html)

    @override_settings(WAGTAIL_POLYMATH={"libraries": [{"url": CUSTOM_JS_URL}]})
    def test_template_tag_omits_integrity(self):
        self.assertInHTML(
            f'<script src="{CUSTOM_JS_URL}" defer></script>',
            polymath_scripts(),
        )

    @override_settings(
        WAGTAIL_POLYMATH={"libraries": [{"url": CUSTOM_JS_URL, "sri": CUSTOM_SRI}]}
    )
    def test_template_tag_uses_custom_url_and_integrity(self):
        self.assertInHTML(
            f'<script src="{CUSTOM_JS_URL}" integrity="{CUSTOM_SRI}" crossorigin="anonymous" defer></script>',
            polymath_scripts(),
        )


class TestStylesheetsTemplateTag(TestCase):
    def test_template_tag_only_outputs_css_if_configured(self):
        self.assertEqual(polymath_stylesheets(), "")

        with override_settings(WAGTAIL_POLYMATH={"engine": "katex"}):
            css = ENGINES["katex"]["libraries"][2]
            self.assertHTMLEqual(
                polymath_stylesheets(),
                f'<link rel="stylesheet" href="{css["url"]}" crossorigin="anonymous" integrity="{css["sri"]}" />',
            )


class TestTemplateTagHelpers(TestCase):
    def test_build_attributes__default(self):
        self.assertEqual(_build_attributes({"url": "foo"}), {"defer": True})

    def test_build_attributes__defer(self):
        self.assertEqual(_build_attributes({"url": "foo"}, defer=False), {})

    def test_build_attributes__with_sri(self):
        lib = ENGINES["mathjax"]["libraries"][0]
        self.assertEqual(
            _build_attributes(lib, defer=True),
            {"crossorigin": "anonymous", "integrity": lib["sri"], "defer": True},
        )


class TestScriptsTemplateTagFontsUrl(TestCase):
    def _init_tag(self):
        return next(
            line
            for line in polymath_scripts().splitlines()
            if "mathjax_init.js" in line
        )

    def test_no_fonts_attribute_by_default(self):
        self.assertNotIn("data-fonts-url", polymath_scripts())

    @override_settings(WAGTAIL_POLYMATH={"fonts_url": "[mathjax]/fonts"})
    def test_init_script_carries_fonts_url(self):
        self.assertIn('data-fonts-url="[mathjax]/fonts"', self._init_tag())

    @override_settings(WAGTAIL_POLYMATH={"fonts_url": '/fonts"><script>'})
    def test_fonts_url_is_escaped(self):
        self.assertIn(
            'data-fonts-url="/fonts&quot;&gt;&lt;script&gt;"', self._init_tag()
        )
