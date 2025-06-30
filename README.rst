``{% nav %}`` tag
=================

.. image:: https://badge.fury.io/py/django-navtag.svg
   :target: https://badge.fury.io/py/django-navtag

.. image:: https://travis-ci.org/SmileyChris/django-navtag.svg?branch=master
   :target: http://travis-ci.org/SmileyChris/django-navtag

.. image:: https://codecov.io/gh/SmileyChris/django-navtag/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/SmileyChris/django-navtag


A simple Django template tag to handle navigation item selection.

.. contents::
    :local:
    :backlinks: none


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

Alternate nav context
~~~~~~~~~~~~~~~~~~~~~

To use a different navigation context variable, prefix the nav item with the variable name:

.. code:: jinja

    {% nav "products" for mainnav %}
    {% nav "settings" for sidenav %}
    
    {% navlink 'mainnav:products' 'product_list' %}Products{% endnavlink %}
    {% navlink 'sidenav:settings' 'user_settings' %}Settings{% endnavlink %}
