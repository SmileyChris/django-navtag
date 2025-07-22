``{% nav %}`` tag
=================

.. image:: https://badge.fury.io/py/django-navtag.svg
   :target: https://badge.fury.io/py/django-navtag

.. image:: https://codecov.io/gh/SmileyChris/django-navtag/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/SmileyChris/django-navtag


A simple Django template tag to handle navigation item selection.

.. contents::
    :local:
    :backlinks: none


Installation
------------

Install the package using pip:

.. code:: bash

    pip install django-navtag

Usage
-----

Add the app to your ``INSTALLED_APPS`` setting:

.. code:: python

    INSTALLED_APPS = (
        # ...
        'django_navtag',
    )

Give your base template a navigation block something like this:

.. code:: jinja

    {% load navtag %}

    {% block nav %}
    {% nav text ' class="selected"' %}
    <ul class="nav">
        <li{{ nav.home }}><a href="/">Home</a></li>
        <li{{ nav.about }}><a href="/about/">About</a></li>
    </ul>
    {% endblock %}

In your templates, extend the base and set the navigation location:

.. code:: jinja

    {% extends "base.html" %}

    {% block nav %}
    {% nav "home" %}
    {{ block.super }}
    {% endblock %}

.. note::
    This works for multiple levels of template inheritance, due to the fact
    that only the first ``{% nav %}`` call found will change the ``nav``
    context variable.


Hierarchical navigation
-----------------------

To create a sub-menu you can check against, simply dot-separate the item:

.. code:: jinja

    {% nav "about_menu.info" %}

This will be pass for both ``{% if nav.about_menu %}`` and
``{% if nav.about_menu.info %}``.


Using a different context variable
----------------------------------

By default, this tag creates a ``nav`` context variable. To use an alternate
context variable name, call ``{% nav [item] for [var_name] %}``:

.. code:: jinja

    {% block nav %}
    {% nav "home" for sidenav %}
    {{ block.super }}
    {% endblock %}


Setting the text output by the nav variable
-------------------------------------------

As shown in the initial example, you can set the text return value of the
``nav`` context variable. Use the format ``{% nav text [content] %}``. For
example:

.. code:: jinja

    {% nav text "active" %}
    <ul>
    <li class="{{ nav.home }}">Home</li>
    <li class="{{ nav.contact }}">Contact</li>
    </ul>

Alternately, you can use boolean comparison of the context variable rather than
text value:

.. code:: jinja

    <section{% if nav.home %} class="wide"{% endif %}>

If using a different context variable name, use the format
``{% nav text [content] for [var_name] %}``.


Comparison operations
---------------------

The ``nav`` object supports comparison operations for more flexible navigation handling:

**Exact matching with** ``==``:

.. code:: jinja

    {% nav "products.phones" %}
    
    {% if nav == "products.phones" %}
        {# True - exact match #}
    {% endif %}
    
    {% if nav == "products" %}
        {# False - not exact #}
    {% endif %}

**Special patterns with** ``!``:

.. code:: jinja

    {% nav "products.electronics" %}
    
    {% if nav == "products!" %}
        {# True - matches any child of products #}
    {% endif %}
    
    {% if nav == "products!clearance" %}
        {# True - matches children except 'clearance' #}
    {% endif %}

**Component checking with** ``in``:

.. code:: jinja

    {% nav "products.electronics.phones" %}
    
    {% if "products" in nav %}
        {# True - component exists #}
    {% endif %}
    
    {% if "electronics" in nav %}
        {# True - component exists #}
    {% endif %}
    
    {% if "tablets" in nav %}
        {# False - component doesn't exist #}
    {% endif %}

These operations also work with sub-navigation:

.. code:: jinja

    {% nav "products.electronics.phones" %}
    
    {% if nav.products == "electronics.phones" %}
        {# True #}
    {% endif %}
    
    {% if "electronics" in nav.products %}
        {# True #}
    {% endif %}


Iteration
---------

The ``nav`` object supports iteration over its active path components:

.. code:: jinja

    {% nav "products.electronics.phones" %}
    
    {% for component in nav %}
        {{ component }}
        {# Outputs: products, electronics, phones #}
    {% endfor %}

This also works with sub-navigation:

.. code:: jinja

    {% nav "products.electronics.phones" %}
    
    {% for component in nav.products %}
        {{ component }}
        {# Outputs: electronics, phones #}
    {% endfor %}


The ``{% navlink %}`` tag
-------------------------

The ``{% navlink %}`` tag provides a convenient way to create navigation links that automatically change based on the active navigation state. It works as a block tag that renders different HTML elements depending on whether the navigation item is active.

Basic usage:

.. code:: jinja

    {% load navtag %}
    
    {% nav text 'active' %}
    {% nav "products" %}
    
    <ul class="nav">
        {% navlink 'home' 'home_url' %}Home{% endnavlink %}
        {% navlink 'products' 'product_list' %}Products{% endnavlink %}
        {% navlink 'contact' 'contact_url' %}Contact{% endnavlink %}
    </ul>

The tag will render:

- ``<a href="..." class="active">...</a>`` - when the nav item is active
- ``<a href="...">...</a>`` - when the nav item is a parent of the active item
- ``<span>...</span>`` - when the nav item is not active

The second parameter uses Django's built-in ``{% url %}`` tag syntax, so you can pass URL names with arguments:

.. code:: jinja

    {% navlink 'product' 'product_detail' product_id=product.id %}
        {{ product.name }}
    {% endnavlink %}

Custom attributes
~~~~~~~~~~~~~~~~~

You can customize the attribute added to active links using ``{% nav text %}`` with an attribute format:

.. code:: jinja

    {% nav text ' aria-selected="true"' %}
    {% nav "home" %}
    
    {% navlink 'home' 'home_url' %}Home{% endnavlink %}
    {# Renders: <a href="/" aria-selected="true">Home</a> #}

Special matching patterns
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``{% navlink %}`` tag supports special patterns for more precise matching:

**Children-only pattern** (``item!``):

.. code:: jinja

    {% nav "courses.special" %}
    
    {% navlink 'courses' 'course_list' %}All Courses{% endnavlink %}
    {# Renders as link with class="active" #}
    
    {% navlink 'courses!' 'course_detail' %}Course Details{% endnavlink %}
    {# Renders as link with class="active" - only when nav is a child of courses #}

When ``courses`` is active (not a child), the first link is active but the second becomes a ``<span>``.

**Exclusion pattern** (``item!exclude``):

.. code:: jinja

    {% nav "courses.special" %}
    
    {% navlink 'courses!list' 'course_detail' %}Course (not list){% endnavlink %}
    {# Renders as link - active for any child except 'list' #}
    
    {% navlink 'courses!special' 'course_detail' %}Course (not special){% endnavlink %}
    {# Renders as span - 'special' is excluded #}

You can also use these patterns with ``{% if %}`` statements:

.. code:: jinja

    {% if nav == "courses!" %}
        {# True - matches any child of courses #}
    {% endif %}

Alternate nav context
~~~~~~~~~~~~~~~~~~~~~

To use a different navigation context variable, prefix the nav item with the variable name:

.. code:: jinja

    {% nav "products" for mainnav %}
    {% nav "settings" for sidenav %}
    
    {% navlink 'mainnav:products' 'product_list' %}Products{% endnavlink %}
    {% navlink 'sidenav:settings' 'user_settings' %}Settings{% endnavlink %}
