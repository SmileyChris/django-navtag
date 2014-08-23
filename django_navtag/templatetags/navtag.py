from django import template
from django.utils import six, safestring
from django.utils.encoding import smart_str, python_2_unicode_compatible


register = template.Library()


@python_2_unicode_compatible
class Nav(object):

    def __init__(self, tree=None, root=None):
        self._root = root or self
        self._tree = tree or {}

    def __getitem__(self, key):
        return Nav(self._tree[key], root=self._root)

    def __str__(self):
        return safestring.mark_safe(six.text_type(self._text))

    def __nonzero__(self):
        return bool(self._tree)

    # Python 3 equivalent.
    __bool__ = __nonzero__

    def _get_text(self):
        if hasattr(self._root, '_text_value'):
            return self._root._text_value
        return self._tree

    def _set_text(self, value):
        self._root._text_value = value

    _text = property(_get_text, _set_text)

    def clear(self):
        self._tree = {}

    def update(self, *args, **kwargs):
        self._tree.update(*args, **kwargs)


class NavNode(template.Node):

    def __init__(self, item=None, var_for=None, var_text=None):
        self.item = item
        self.var_name = var_for or 'nav'
        self.text = var_text

    def render(self, context):
        first_context_stack = context.dicts[0]
        nav = first_context_stack.get(self.var_name)
        if nav is not context.get(self.var_name):
            raise template.TemplateSyntaxError(
                "'{0}' variable has been altered in current context"
                .format(self.var_name))

        if not isinstance(nav, Nav):
            nav = Nav()
            # Copy the stack to avoid leaking into other contexts.
            new_first_context_stack = first_context_stack.copy()
            new_first_context_stack[self.var_name] = nav
            context.dicts[0] = new_first_context_stack

        if self.text:
            nav._text = self.text.resolve(context)
            return ''

        # If self.item was blank then there's nothing else to do here.
        if not self.item:
            return ''

        if nav:
            # If the nav variable is already set, don't do anything.
            return ''

        item = self.item.resolve(context)
        item = item and smart_str(item)
        value = True
        if not item:
            item = ''
        for part in reversed(item.split('.')):
            new_item = {}
            new_item[part] = value
            value = new_item

        nav.clear()
        nav.update(new_item)
        return ''

    def __repr__(self):
        return "<Nav node>"


@register.tag
def nav(parser, token):
    """
    Handles navigation item selection.

    Example usage::

        {# Set the context so {{ nav.home }} (or {{ mynav.home }}) is True #}
        {% nav "home" %} or {% nav "home" for mynav %}

    The most basic (and common) use of the tag is to call ``{% nav [item] %}``,
    where ``[item]`` is the item you want to check is selected.

    By default, this tag creates a ``nav`` context variable. To use an
    alternate context variable name, call ``{% nav [item] for [var_name] %}``.

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

    As a shortcut, you can use a ``text`` argument and then just reference the
    variable rather than query it with an ``{% if %}`` tag::

        {% nav text ' class="active"' %}
        <ul class="nav">
            <li{{ nav.home }}><a href="/">Home</a></li>
            <li{{ nav.about }}><a href="/about/">About</a></li>
        </ul>

    To create a sub-menu you can check against, simply dot-separate the item::

        {% nav "about_menu.info" %}

    This will be pass for both ``{% if nav.about_menu %}`` and
    ``{% if nav.about_menu.info %}``.
    """
    bits = token.split_contents()

    ok = True
    keys = {'for': False, 'text': True}
    node_kwargs = {}
    while len(bits) > 2:
        value = bits.pop()
        key = bits.pop()
        if key not in keys:
            ok = False
            break
        compile_filter = keys.pop(key)
        if compile_filter:
            value = parser.compile_filter(value)
        node_kwargs['var_{0}'.format(key)] = value

    if len(bits) > 1:
        # Text argument doesn't expect an item.
        ok = 'text' not in node_kwargs
        item = parser.compile_filter(bits[1])
    else:
        item = None

    if not ok:
        raise template.TemplateSyntaxError(
            'Unexpected format for %s tag' % bits[0])

    return NavNode(item, **node_kwargs)
