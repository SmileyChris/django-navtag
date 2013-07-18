from django import template
from django.utils.encoding import smart_str


register = template.Library()


class NavNode(template.Node):

    def __init__(self, item=None, var_name=None):
        self.item = item
        self.var_name = var_name or 'nav'

    def render(self, context):
        # If the nav variable is already set (to a non-empty value), don't do
        # anything.
        if context.get(self.var_name):
            return ''
        # If self.item was blank, just set the nav variable to the context
        # (useful to put the nav in a higher context stack)
        if not self.item:
            context[self.var_name] = {}
            return ''
        item = self.item.resolve(context)
        item = item and smart_str(item)
        if not item:
            return ''
        value = True
        for part in reversed(item.split('.')):
            new_item = {}
            new_item[part] = value
            value = new_item
        # The nav variable could have been set (as an empty dict) on a higher
        # context stack. Try getting it from the context, otherwise set it to
        # the current context stack.
        nav = context.get(self.var_name)
        if not isinstance(nav, dict):
            nav = {}
            context[self.var_name] = nav
        nav.update(new_item)
        return ''

    def __repr__(self):
        return "<Nav node>"


@register.tag
def nav(parser, token):
    """
    Handles navigation item selection.

    Example usage::

        {# Set up the variable for use across context-stacking tags #}
        {% nav %} or {% nav for mynav %}

        {# Set the context so {{ nav.home }} (or {{ mynav.home }}) is True #}
        {% nav "home" %} or {% nav "home" for mynav %}

    The most basic (and common) use of the tag is to call ``{% nav [item] %}``,
    where ``[item]`` is the item you want to check is selected.

    By default, this tag creates a ``nav`` context variable. To use an
    alternate context variable name, call ``{% nav [item] for [var_name] %}``.

    To use this tag across ``{% block %}`` tags (or other context-stacking
    template tags such as ``{% for %}``), call the tag without specifying an
    item.

    Your HTML navigation template should look something like::

        {% block nav %}
        <ul class="nav">
            <li{% if nav.home %} class="selected"{% endif %}>
                <a href="/">Home</a>
            </li>
            <li{% if nav.about %} class="selected"{% endif %}>
                <a href="/about/">About</a>
            </li>
        </ul>
        {% endblock %}

    To override this in a child template, you'd do::

        {% include "base.html" %}
        {% load nav %}

        {% block nav %}
        {% nav "about" %}
        {{ block.super }}
        {% endblock %}

    This works for multiple levels of template inheritance, due to the fact
    that the tag only does anything if the ``nav`` context variable does not
    exist. So only the first ``{% nav %}`` call found will ever be processed.

    To create a sub-menu you can check against, simply dot-separate the item::

        {% nav "about_menu.info" %}

    This will be pass for both ``{% if nav.about_menu %}`` and
    ``{% if nav.about_menu.info %}``.
    """
    bits = token.split_contents()
    if len(bits) > 2:
        var_name = bits.pop()
        for_bit = bits.pop()
        if for_bit != 'for' or len(bits) > 2:
            raise template.TemplateSyntaxError('Unexpected format for %s tag' %
                                               bits[0])
    else:
        var_name = 'nav'
    if len(bits) > 1:
        item = parser.compile_filter(bits[1])
    else:
        item = None
    return NavNode(item, var_name)
