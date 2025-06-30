from django import template
from django.template.loader import render_to_string
from django.test import TestCase
from django.utils.html import escape

from django_navtag.templatetags.navtag import NavNode

BASIC_TEMPLATE = """
{% load navtag %}
{% nav "banana" %}
{% if nav.apple %}Apple{% endif %}
{% if nav.banana %}Banana{% endif %}
"""

FOR_TEMPLATE = """
{% load navtag %}
{% nav "banana" for othernav %}
{% if othernav.apple %}Apple{% endif %}
{% if othernav.banana %}Banana{% endif %}
"""

NAV_LINK_TEMPLATE = """
{% load navtag %}
{% nav text 'active' %}
{% nav "products" %}
{% navlink 'home' 'home' %}Home{% endnavlink %}
{% navlink 'products' 'products' %}Products{% endnavlink %}
{% navlink 'about' 'about' %}About{% endnavlink %}
"""

NAV_LINK_TEXT_TEMPLATE = """
{% load navtag %}
{% nav text "selected" %}
{% nav "products" %}
{% navlink 'home' 'home' %}Home{% endnavlink %}
{% navlink 'products' 'products' %}Products{% endnavlink %}
{% navlink 'about' 'about' %}About{% endnavlink %}
"""


class NavTagTest(TestCase):
    def test_basic(self):
        t = template.Template(BASIC_TEMPLATE)
        content = t.render(template.Context()).strip()
        self.assertNotIn("Apple", content)
        self.assertIn("Banana", content)

    def test_for(self):
        t = template.Template(FOR_TEMPLATE)
        content = t.render(template.Context()).strip()
        self.assertNotIn("Apple", content)
        self.assertIn("Banana", content)

    def test_basic_extends(self):
        content = render_to_string("navtag_tests/home.txt").strip()
        self.assertIn("- Home (active)", content)
        self.assertNotIn("- Contact (active)", content)

        content = render_to_string("navtag_tests/contact.txt").strip()
        self.assertNotIn("- Home (active)", content)
        self.assertIn("- Contact (active)", content)

    def test_unset(self):
        content = render_to_string("navtag_tests/home.txt").strip()
        self.assertIn("- Home (active)", content)
        self.assertNotIn("- Contact (active)", content)

        content = render_to_string("navtag_tests/home-unset.txt").strip()
        self.assertNotIn("- Home (active)", content)
        self.assertNotIn("- Contact (active)", content)

    def test_heirarchical(self):
        content = render_to_string("navtag_tests/submenu/home.txt").strip()
        self.assertIn("- Home (active)", content)
        self.assertNotIn("- Fruit (active)", content)
        self.assertNotIn("  - Apple (active)", content)
        self.assertNotIn("  - Banana (active)", content)

        content = render_to_string("navtag_tests/submenu/base_fruit.txt").strip()
        self.assertNotIn("- Home (active)", content)
        self.assertIn("- Fruit (active)", content)
        self.assertNotIn("  - Apple (active)", content)
        self.assertNotIn("  - Banana (active)", content)

        content = render_to_string("navtag_tests/submenu/apple.txt").strip()
        self.assertNotIn("- Home (active)", content)
        self.assertIn("- Fruit (active)", content)
        self.assertIn("  - Apple (active)", content)
        self.assertNotIn("  - Banana (active)", content)

        content = render_to_string("navtag_tests/submenu/banana.txt").strip()
        self.assertNotIn("- Home (active)", content)
        self.assertIn("- Fruit (active)", content)
        self.assertNotIn("  - Apple (active)", content)
        self.assertIn("  - Banana (active)", content)

    def test_top_context(self):
        content = render_to_string("navtag_tests/context/home.txt").strip()
        self.assertIn("- Home (active)", content)
        self.assertIn("HOME", content)

    def test_repr(self):
        node = NavNode()
        self.assertEqual(repr(node), "<Nav node>")

    def test_invalid_args(self):
        self.assertRaises(
            template.TemplateSyntaxError,
            template.Template,
            """{% load navtag %}{% nav 'test' unexpected %}""",
        )

    def test_backwards_compatible_empty_tag(self):
        content = template.Template("{% load navtag %}{% nav %}").render(
            template.Context()
        )
        self.assertEqual(content, "")

        content = template.Template("{% load navtag %}{% nav for sidenav %}").render(
            template.Context()
        )
        self.assertEqual(content, "")

    def test_yell_if_context_variable_changed(self):
        t = template.Template('{% load navtag %}{% nav "test" %}{{ nav }}')
        c = template.Context({"nav": "anything"})
        c.update({"nav": "test"})
        self.assertRaises(template.TemplateSyntaxError, t.render, c)

    def test_nav_text(self):
        content = template.Template('{% load navtag %}{% nav text "THIS" %}').render(
            template.Context()
        )
        self.assertEqual(content, "")

    def test_nav_text_none(self):
        content = render_to_string("navtag_tests/text/base.txt").strip()
        self.assertEqual(content, "- Home\n- Contact")

    def test_nav_text_set(self):
        content = render_to_string("navtag_tests/text/home.txt").strip()
        self.assertIn("Home [is active]", content)
        self.assertNotIn("Contact [is active]", content)

        content = render_to_string("navtag_tests/text/contact.txt").strip()
        self.assertNotIn("Home [is active]", content)
        self.assertIn("Contact [is active]", content)

    def test_nav_default_text(self):
        content = (
            template.Template(
                '{% load navtag %}{% nav "fruit" %}{{ nav.fruit }}'
            ).render(template.Context(autoescape=False))
        ).strip()
        self.assertEqual(content, "True")

        content = (
            template.Template(
                '{% load navtag %}{% nav "fruit.banana" %}{{ nav.fruit }}'
            ).render(template.Context(autoescape=False))
        ).strip()
        self.assertEqual(content, "{'banana': True}")

    def test_escaping(self):
        content = (
            template.Template(
                """{% load navtag %}{% nav text ' class="active"' %}"""
                "<p{{ nav }}>{{ name }}</p>"
            ).render(template.Context({"name": "Mc'D"}))
        ).strip()
        escaped = escape("Mc'D")
        self.assertEqual(content, """<p class="active">%s</p>""" % escaped)
    
    def test_navlink_active(self):
        """Test navlink when the nav item is active"""
        # Mock URL resolution
        def mock_url_tag_render(context):
            return "/products/"
        
        t = template.Template(NAV_LINK_TEMPLATE)
        # We need to patch the url rendering since we don't have URL conf
        from django_navtag.templatetags.navtag import NavLinkNode
        original_render = NavLinkNode.render
        
        def patched_render(self, context):
            # Override URL node rendering
            original_url_render = self.url_node.render
            self.url_node.render = lambda ctx: {
                'home': '/home/',
                'products': '/products/', 
                'about': '/about/'
            }.get(self.nav_item.resolve(ctx), '/')
            result = original_render(self, context)
            self.url_node.render = original_url_render
            return result
        
        NavLinkNode.render = patched_render
        try:
            content = t.render(template.Context()).strip()
            # Products should be active with class="active"
            self.assertIn('<a href="/products/" class="active">Products</a>', content)
            # Home and About should be spans since they're not set in nav
            self.assertIn('<span>Home</span>', content)
            self.assertIn('<span>About</span>', content)
        finally:
            NavLinkNode.render = original_render
    
    def test_navlink_inactive(self):
        """Test navlink when no nav item is active"""
        t = template.Template("""
{% load navtag %}
{% navlink 'home' 'home' %}Home{% endnavlink %}
{% navlink 'products' 'products' %}Products{% endnavlink %}
""")
        from django_navtag.templatetags.navtag import NavLinkNode
        original_render = NavLinkNode.render
        
        def patched_render(self, context):
            # Override URL node rendering
            original_url_render = self.url_node.render
            self.url_node.render = lambda ctx: '/' + self.nav_item.resolve(ctx) + '/'
            result = original_render(self, context)
            self.url_node.render = original_url_render
            return result
        
        NavLinkNode.render = patched_render
        try:
            content = t.render(template.Context()).strip()
            # All items should be spans since no nav is set
            self.assertIn('<span>Home</span>', content)
            self.assertIn('<span>Products</span>', content)
            # No links should be present
            self.assertNotIn('<a', content)
        finally:
            NavLinkNode.render = original_render
    
    def test_navlink_with_custom_text(self):
        """Test navlink with custom nav text"""
        from django_navtag.templatetags.navtag import NavLinkNode
        original_render = NavLinkNode.render
        
        def patched_render(self, context):
            # Override URL node rendering
            original_url_render = self.url_node.render
            self.url_node.render = lambda ctx: '/' + self.nav_item.resolve(ctx) + '/'
            result = original_render(self, context)
            self.url_node.render = original_url_render
            return result
        
        NavLinkNode.render = patched_render
        try:
            t = template.Template(NAV_LINK_TEXT_TEMPLATE)
            content = t.render(template.Context()).strip()
            # With nav text "selected", products should have class="selected"
            self.assertIn('<a href="/products/" class="selected">Products</a>', content)
            # Others should be spans since they're not set in nav
            self.assertIn('<span>Home</span>', content)
            self.assertIn('<span>About</span>', content)
            # No items should have class="active" since text is "selected"
            self.assertNotIn('class="active"', content)
        finally:
            NavLinkNode.render = original_render
    
    def test_navlink_hierarchical(self):
        """Test navlink with hierarchical navigation"""
        t = template.Template("""
{% load navtag %}
{% nav text ' class="active"' %}
{% nav "products.electronics" %}
{% navlink 'products' 'products' %}All Products{% endnavlink %}
{% navlink 'products.electronics' 'electronics' %}Electronics{% endnavlink %}
{% navlink 'products.clothing' 'clothing' %}Clothing{% endnavlink %}
""")
        from django_navtag.templatetags.navtag import NavLinkNode
        original_render = NavLinkNode.render
        
        def patched_render(self, context):
            # Override URL node rendering
            original_url_render = self.url_node.render
            self.url_node.render = lambda ctx: '/' + self.nav_item.resolve(ctx).replace('.', '/') + '/'
            result = original_render(self, context)
            self.url_node.render = original_url_render
            return result
        
        NavLinkNode.render = patched_render
        try:
            content = t.render(template.Context()).strip()
            # According to the implementation, both parent and exact match get class="active"
            self.assertIn('<a href="/products/" class="active">All Products</a>', content)
            # products.electronics should be active (exact match)
            self.assertIn('<a href="/products/electronics/" class="active">Electronics</a>', content)
            # products.clothing should be a span
            self.assertIn('<span>Clothing</span>', content)
        finally:
            NavLinkNode.render = original_render
    
    def test_navlink_with_attribute_text(self):
        """Test navlink with nav text containing '=' (e.g., data attributes)"""
        t = template.Template("""
{% load navtag %}
{% nav text ' aria-selected="true"' %}
{% nav "products" %}
{% navlink 'home' 'home' %}Home{% endnavlink %}
{% navlink 'products' 'products' %}Products{% endnavlink %}
""")
        from django_navtag.templatetags.navtag import NavLinkNode
        original_render = NavLinkNode.render
        
        def patched_render(self, context):
            # Override URL node rendering
            original_url_render = self.url_node.render
            self.url_node.render = lambda ctx: '/' + self.nav_item.resolve(ctx) + '/'
            result = original_render(self, context)
            self.url_node.render = original_url_render
            return result
        
        NavLinkNode.render = patched_render
        try:
            content = t.render(template.Context()).strip()
            # Products should have the data attribute
            self.assertIn('<a href="/products/" aria-selected="true">Products</a>', content)
            # Home should be a span
            self.assertIn('<span>Home</span>', content)
            # Should not contain class= since we're using data attributes
            self.assertNotIn('class=', content)
        finally:
            NavLinkNode.render = original_render
