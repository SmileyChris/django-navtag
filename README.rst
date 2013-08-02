``{% nav %}`` tag
=================

A simple Django template tag to handle navigation item selection.

.. image:: https://secure.travis-ci.org/SmileyChris/django-navtag.png?branch=master
   :target: http://travis-ci.org/SmileyChris/django-navtag

Example
-------

Add the app to your ``INSTALLED_APPS`` setting::

	INSTALLED_APPS = (
		# ...
		'django_navtag',
	)

Give your base template a navigation block something like this::

    {% load navtag %}

    {% block nav %}
    {% nav text ' class="selected"' %}
    <ul class="nav">
        <li{{ nav.home }}><a href="/">Home</a></li>
        <li{{ nav.about }}><a href="/about/">About</a></li>
    </ul>
    {% endblock %}

In your templates, extend the base and set the navigation location::

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

To create a sub-menu you can check against, simply dot-separate the item::

    {% nav "about_menu.info" %}

This will be pass for both ``{% if nav.about_menu %}`` and
``{% if nav.about_menu.info %}``.


Using a different context variable
----------------------------------

By default, this tag creates a ``nav`` context variable. To use an alternate
context variable name, call ``{% nav [item] for [var_name] %}``::

	{% block nav %}
	{% nav "home" for sidenav %}
	{{ block.super }}
	{% endblock %}


Setting the text output by the nav variable
-------------------------------------------

As shown in the initial example, you can set the text return value of the
``nav`` context variable. Use the format ``{% nav text [content] %}``. For
example::

    {% nav text "active" %}
    <ul>
    <li class="{{ nav.home }}">Home</li>
    <li class="{{ nav.contact }}">Contact</li>
    </ul>

Alternately, you can use boolean comparison of the context variable rather than
text value::

    <section{% if nav.home %} class="wide"{% endif %}>

If using a different context variable name, use the format
``{% nav text [content] for [var_name] %}``.
