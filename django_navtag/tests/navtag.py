from django.test import TestCase
from django import template
from django.template.loader import render_to_string


BASIC_TEMPLATE = '''
{% load navtag %}
{% nav "banana" %}
{% if nav.apple %}Apple{% endif %}
{% if nav.banana %}Banana{% endif %}
'''


class NavTagTest(TestCase):

    def test_basic(self):
        t = template.Template(BASIC_TEMPLATE)
        content = t.render(template.Context())
        self.assertNotIn('Apple', content)
        self.assertIn('Banana', content)

    def test_basic_extends(self):
        content = render_to_string('navtag_tests/home.html')
        self.assertIn('- Home (active)', content)
        self.assertNotIn('- Contact (active)', content)

        content = render_to_string('navtag_tests/contact.html')
        self.assertNotIn('- Home (active)', content)
        self.assertIn('- Contact (active)', content)

    def test_heirarchical(self):
        content = render_to_string('navtag_tests/submenu/home.html')
        self.assertIn('- Home (active)', content)
        self.assertNotIn('- Fruit (active)', content)
        self.assertNotIn('  - Apple (active)', content)
        self.assertNotIn('  - Banana (active)', content)

        content = render_to_string('navtag_tests/submenu/apple.html')
        self.assertNotIn('- Home (active)', content)
        self.assertIn('- Fruit (active)', content)
        self.assertIn('  - Apple (active)', content)
        self.assertNotIn('  - Banana (active)', content)

        content = render_to_string('navtag_tests/submenu/banana.html')
        self.assertNotIn('- Home (active)', content)
        self.assertIn('- Fruit (active)', content)
        self.assertNotIn('  - Apple (active)', content)
        self.assertIn('  - Banana (active)', content)
