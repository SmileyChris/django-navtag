import setuptools

setuptools.setup(
    name='django-navtag',
    version='1.0',
    description=("A simple Django navigation template tag"),
    author='Chris Beaven',
    author_email='smileychris@gmail.com',
    url='http://github.com/SmileyChris/django-navtag',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
