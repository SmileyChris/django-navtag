from django import template
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe

register = template.Library()


class Nav(object):
    def __init__(self, tree=None, root=None):
        self._root = root or self
        self._tree = tree or {}

    def __getitem__(self, key):
        return Nav(self._tree[key], root=self._root)

    def __str__(self):
        return mark_safe(str(self._text))

    def __bool__(self):
        return bool(self._tree)

    def _get_text(self):
        if hasattr(self._root, "_text_value"):
            return self._root._text_value
        return self._tree

    def _set_text(self, value):
        self._root._text_value = value

    _text = property(_get_text, _set_text)

    def clear(self):
        self._tree = {}

    def update(self, *args, **kwargs):
        self._tree.update(*args, **kwargs)
    
    def get_active_path(self, path=''):
        """Get the dotted path of the active navigation item"""
        for key, value in self._tree.items():
            current_path = path + '.' + key if path else key
            if isinstance(value, dict):
                # Recurse into nested nav
                sub_nav = Nav(value, root=self._root)
                result = sub_nav.get_active_path(current_path)
                if result:
                    return result
            elif value:
                return current_path
        return ''
    
    def __eq__(self, other):
        """Check if the active navigation path matches the given pattern
        
        Patterns:
        - "item" - exact match
        - "item!" - children only (not exact match)
        - "item!exclude" - children except 'exclude'
        """
        if isinstance(other, str):
            active_path = self.get_active_path()
            
            if '!' in other:
                parts = other.split('!', 1)
                parent = parts[0]
                exclude = parts[1] if len(parts) > 1 and parts[1] else None
                
                if exclude:
                    # Pattern like 'courses!list' - match children except specific ones
                    return (active_path.startswith(parent + '.') and 
                            active_path != parent and
                            not active_path.startswith(parent + '.' + exclude))
                else:
                    # Pattern like 'courses!' - match children only, not exact
                    return active_path.startswith(parent + '.') and active_path != parent
            else:
                # Normal pattern - exact match
                return active_path == other
        elif isinstance(other, Nav):
            return self.get_active_path() == other.get_active_path()
        return False
    
    def __contains__(self, item):
        """Check if a component is part of the active navigation path"""
        if isinstance(item, str):
            active_path = self.get_active_path()
            if not active_path:
                return False
            # Check if the component matches any part of the path
            components = active_path.split('.')
            return item in components
        return False


class NavNode(template.Node):
    def __init__(self, item=None, var_for=None, var_text=None):
        self.item = item
        self.var_name = var_for or "nav"
        self.text = var_text

    def render(self, context):
        first_context_stack = context.dicts[0]
        nav = first_context_stack.get(self.var_name)
        if nav is not context.get(self.var_name):
            raise template.TemplateSyntaxError(
                "'{0}' variable has been altered in current context".format(
                    self.var_name
                )
            )

        if not isinstance(nav, Nav):
            nav = Nav()
            # Copy the stack to avoid leaking into other contexts.
            new_first_context_stack = first_context_stack.copy()
            new_first_context_stack[self.var_name] = nav
            context.dicts[0] = new_first_context_stack

        if self.text:
            nav._text = self.text.resolve(context)
            return ""

        # If self.item was blank then there's nothing else to do here.
        if not self.item:
            return ""

        if nav:
            # If the nav variable is already set, don't do anything.
            return ""

        item = self.item.resolve(context)
        item = item and smart_str(item)
        value = True
        if not item:
            item = ""
        for part in reversed(item.split(".")):
            new_item = {}
            new_item[part] = value
            value = new_item

        nav.clear()
        nav.update(new_item)
        return ""

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

    Comparison operations::

        {# Exact path matching with == #}
        {% if nav == "home" %}              {# True if exactly "home" is active #}
        {% if nav == "products.phones" %}   {# True if exactly "products.phones" is active #}
        
        {# Children-only matching #}
        {% if nav == "products!" %}         {# True if any child of products is active #}
        {% if nav == "products!list" %}     {# True if child of products except 'list' #}
        
        {# Component checking with 'in' #}
        {% if "products" in nav %}          {# True if active path contains "products" #}
        {% if "phones" in nav %}            {# True if active path contains "phones" #}

        {# Also works on sub-navigation #}
        {% nav "products.electronics.phones" %}
        {% if nav.products == "electronics.phones" %}  {# True #}
        {% if "electronics" in nav.products %}         {# True #}
    """
    bits = token.split_contents()

    ok = True
    keys = {"for": False, "text": True}
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
        node_kwargs["var_{0}".format(key)] = value

    if len(bits) > 1:
        # Text argument doesn't expect an item.
        ok = "text" not in node_kwargs
        item = parser.compile_filter(bits[1])
    else:
        item = None

    if not ok:
        raise template.TemplateSyntaxError("Unexpected format for %s tag" % bits[0])

    return NavNode(item, **node_kwargs)


class NavLinkNode(template.Node):
    def __init__(self, nav_item, url_node, nodelist):
        self.nav_item = nav_item
        self.url_node = url_node
        self.nodelist = nodelist

    def render(self, context):
        nav_item = self.nav_item.resolve(context)
        
        # Check if alternate nav variable specified with ':'
        var_name = "nav"
        if ':' in nav_item:
            var_name, nav_item = nav_item.split(':', 1)
        
        nav = context.get(var_name)
        if not isinstance(nav, Nav):
            nav = Nav()
        
        # Check if nav item is active
        try:
            # For normal patterns, check both exact match and parent match
            # For special patterns (with !), use the Nav's __eq__ method
            if '!' in nav_item:
                # Use Nav's __eq__ for special patterns
                is_link = nav == nav_item
            else:
                # Normal pattern - exact match or parent match
                active_path = nav.get_active_path() if nav else ''
                is_exact_match = active_path == nav_item
                is_parent_match = active_path.startswith(nav_item + '.')
                is_link = is_exact_match or is_parent_match
            
            # Get the text value
            nav_text = ''
            if is_link and hasattr(nav, '_text_value') and nav._text_value:
                nav_text = nav._text_value
                if "=" not in nav_text:
                    nav_text = ' class="{}"'.format(nav_text.strip())
        except (KeyError, AttributeError):
            is_link = False
            nav_text = ""
        
        # Get the URL from the url node
        url = self.url_node.render(context)
        
        # Get the content inside the block
        content = self.nodelist.render(context)
        
        # Determine which element to render
        if is_link:
            # Truthy but not exact - render as regular link
            return '<a href="{}"{}>{}</a>'.format(url, nav_text, content)
        else:
            # Falsy - render as span
            return '<span>{}</span>'.format(content)


@register.tag
def navlink(parser, token):
    """
    Renders a link that changes based on navigation state.
    
    Usage::
        
        {% nav text ' class="active"' %}
        {% navlink 'products' 'products:list' %}Products{% endnavlink %}
    
    Renders as:
    - <a href="/products/" class="active">Products</a> - if nav.products is the active item
    - <a href="/products/">Products</a> - if nav.products is a parent item of nav
    - <span>Products</span> - if nav.products doesn't match

    Special patterns::
    
        {% navlink 'courses!' 'course_detail' %}Course Details{% endnavlink %}
        {# Active only for children like 'courses.special', not 'courses' itself #}
        
        {% navlink 'courses!list' 'course_detail' %}Course (not list){% endnavlink %}
        {# Active for 'courses.special' but not 'courses.list' #}

    Use {% navlink 'alt_nav:products' ... %} to specify a different nav context.
    """
    from django.template.defaulttags import url

    bits = token.split_contents()
    
    if len(bits) < 3:
        raise template.TemplateSyntaxError(
            "{} tag requires at least two arguments: nav item and url name".format(bits[0])
        )
    
    # First argument is the nav item
    nav_item = parser.compile_filter(bits[1])
    
    # The rest is passed to the url tag
    url_bits = ['url'] + bits[2:]
    url_token = token.__class__(token.token_type, ' '.join(url_bits), token.position, token.lineno)
    
    url_node = url(parser, url_token)
    
    # Parse until endnavlink
    nodelist = parser.parse(('endnavlink',))
    parser.delete_first_token()
    
    return NavLinkNode(nav_item, url_node, nodelist)
