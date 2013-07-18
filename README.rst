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

In your templates, extend the base and set the navigation location::

	{% extends "base.html" %}

	{% block nav %}
	{% nav "home" %}
	{{ block.super }}
	{% endblock %}

.. note::
    This works for multiple levels of template inheritance, due to the fact
    that the tag only does anything if the ``nav`` context variable does not
    exist. So only the first ``{% nav %}`` call found will ever be processed.


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
