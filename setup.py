import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-signal-notifier',
    version='0.1',
    packages=['django_signal_notifier'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A Django app to send message or notification based on a signal triggering.',
    long_description=README,
    zip_safe=False,
    url="https://gitlab.com/hadiazaddel/django-signal-notifier",
    keywords=["django", "notification", "signal"],
    author="Mohammad Hadi Azaddel",
    author_email="m.h.azaddel@gmail.com",
    install_requires=["Django>=1.8"],
    project_urls={
        'Documentation': 'https://gitlab.com/hadiazaddel/django-signal-notifier',
        'Source': 'https://gitlab.com/hadiazaddel/django-signal-notifier',
        'Tracker': 'https://gitlab.com/hadiazaddel/django-signal-notifier/issues',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)
