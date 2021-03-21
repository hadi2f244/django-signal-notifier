import os
from setuptools import setup
from django_signal_notifier import VERSION

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-signal-notifier',
    version='.'.join(map(str, VERSION)),
    packages=['django_signal_notifier'],
    include_package_data=True,
    license='BSD-3-Clause',
    description="DSN or django-signal-notifier is a Django package to send message or notification based on the "
                "Django's signals triggering",
    long_description=README,
    zip_safe=False,
    url="https://github.com/hadi2f244/django-signal-notifier",
    keywords=["django", "notification", "signal"],
    author="Mohammad Hadi Azaddel",
    author_email="m.h.azaddel@gmail.com",
    install_requires=["Django>=1.8,<3.1"
                      "Telethon>=1.16.4"],
    project_urls={
        'Documentation': 'https://django-signal-notifier.readthedocs.io/',
        'Source': 'https://github.com/hadi2f244/django-signal-notifier',
        'Tracker': 'https://github.com/hadi2f244/django-signal-notifier/issues',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
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
