from django import template
from django.test import TestCase
from django.template.loader import render_to_string

from django_navtag.templatetags.navtag import NavNode

BASIC_TEMPLATE = '''
{% load navtag %}
{% nav "banana" %}
{% if nav.apple %}Apple{% endif %}
{% if nav.banana %}Banana{% endif %}
'''

FOR_TEMPLATE = '''
{% load navtag %}
{% nav "banana" for othernav %}
{% if othernav.apple %}Apple{% endif %}
{% if othernav.banana %}Banana{% endif %}
'''


class NavTagTest(TestCase):

    def test_basic(self):
        t = template.Template(BASIC_TEMPLATE)
        content = t.render(template.Context()).strip()
        self.assertNotIn('Apple', content)
        self.assertIn('Banana', content)

    def test_for(self):
        t = template.Template(FOR_TEMPLATE)
        content = t.render(template.Context()).strip()
        self.assertNotIn('Apple', content)
        self.assertIn('Banana', content)

    def test_basic_extends(self):
        content = render_to_string('navtag_tests/home.txt').strip()
        self.assertIn('- Home (active)', content)
        self.assertNotIn('- Contact (active)', content)

        content = render_to_string('navtag_tests/contact.txt').strip()
        self.assertNotIn('- Home (active)', content)
        self.assertIn('- Contact (active)', content)

    def test_unset(self):
        content = render_to_string('navtag_tests/home.txt').strip()
        self.assertIn('- Home (active)', content)
        self.assertNotIn('- Contact (active)', content)

        content = render_to_string('navtag_tests/home-unset.txt').strip()
        self.assertNotIn('- Home (active)', content)
        self.assertNotIn('- Contact (active)', content)

    def test_heirarchical(self):
        content = render_to_string('navtag_tests/submenu/home.txt').strip()
        self.assertIn('- Home (active)', content)
        self.assertNotIn('- Fruit (active)', content)
        self.assertNotIn('  - Apple (active)', content)
        self.assertNotIn('  - Banana (active)', content)

        content = render_to_string(
            'navtag_tests/submenu/base_fruit.txt').strip()
        self.assertNotIn('- Home (active)', content)
        self.assertIn('- Fruit (active)', content)
        self.assertNotIn('  - Apple (active)', content)
        self.assertNotIn('  - Banana (active)', content)

        content = render_to_string('navtag_tests/submenu/apple.txt').strip()
        self.assertNotIn('- Home (active)', content)
        self.assertIn('- Fruit (active)', content)
        self.assertIn('  - Apple (active)', content)
        self.assertNotIn('  - Banana (active)', content)

        content = render_to_string('navtag_tests/submenu/banana.txt').strip()
        self.assertNotIn('- Home (active)', content)
        self.assertIn('- Fruit (active)', content)
        self.assertNotIn('  - Apple (active)', content)
        self.assertIn('  - Banana (active)', content)

    def test_top_context(self):
        content = render_to_string('navtag_tests/context/home.txt').strip()
        self.assertIn('- Home (active)', content)
        self.assertIn('HOME', content)

    def test_repr(self):
        node = NavNode()
        self.assertEqual(repr(node), "<Nav node>")

    def test_invalid_args(self):
        self.assertRaises(
            template.TemplateSyntaxError, template.Template,
            '''{% load navtag %}{% nav 'test' unexpected %}''')

    def test_backwards_compatible_empty_tag(self):
        content = template.Template(
            '{% load navtag %}{% nav %}').render(template.Context())
        self.assertEqual(content, '')

        content = template.Template(
            '{% load navtag %}{% nav for sidenav %}').render(template.Context())
        self.assertEqual(content, '')

    def test_yell_if_context_variable_changed(self):
        t = template.Template('{% load navtag %}{% nav "test" %}{{ nav }}')
        c = template.Context({'nav': 'anything'})
        c.update({'nav': 'test'})
        self.assertRaises(
            template.TemplateSyntaxError,
            t.render, c)
