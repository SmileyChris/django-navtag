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

    def test_nav_text(self):
        content = (
            template.Template('{% load navtag %}{% nav text "THIS" %}')
            .render(template.Context()))
        self.assertEqual(content, '')

    def test_nav_text_none(self):
        content = render_to_string('navtag_tests/text/base.txt').strip()
        self.assertEqual(content, '- Home\n- Contact')

    def test_nav_text_set(self):
        content = render_to_string('navtag_tests/text/home.txt').strip()
        self.assertIn('Home [is active]', content)
        self.assertNotIn('Contact [is active]', content)

        content = render_to_string('navtag_tests/text/contact.txt').strip()
        self.assertNotIn('Home [is active]', content)
        self.assertIn('Contact [is active]', content)

    def test_nav_default_text(self):
        content = (
            template.Template(
                '{% load navtag %}{% nav "fruit" %}{{ nav.fruit }}')
            .render(template.Context(autoescape=False))).strip()
        self.assertEqual(content, "True")

        content = (
            template.Template(
                '{% load navtag %}{% nav "fruit.banana" %}{{ nav.fruit }}')
            .render(template.Context(autoescape=False))).strip()
        self.assertEqual(content, "{'banana': True}")

    def test_escaping(self):
        content = (
            template.Template(
                '''{% load navtag %}{% nav text ' class="active"' %}'''
                '<p{{ nav }}>{{ name }}</p>')
            .render(template.Context({'name': "Mc'D"}))).strip()
        self.assertEqual(content, '''<p class="active">Mc&#39;D</p>''')
