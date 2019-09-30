# Trackathon
### Share-a-thon pledge tracking.

This Python/Django project aims to take data in from the pledge process and display information on the pledges received.

Built with Python 3.7.0 and Django 2.2.4

Requires:
- [django-tagging](https://pypi.python.org/pypi/django-tagging/)
- [django-tagging-autocomplete](https://pypi.python.org/pypi/django-tagging-autocomplete)


Need to manually edit .\site-packages\tagging_autocomplete\widgets.py to change django.core.urlresolvers to django.urls as well as the def for render() to include renderer=None