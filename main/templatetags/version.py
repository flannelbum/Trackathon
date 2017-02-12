from django import template
from django.conf import settings
import time
import os

register = template.Library()

@register.simple_tag
def version_date():
    return time.strftime('%m%d%Y_%H%M', time.gmtime(os.path.getmtime(settings.BASE_DIR + '/.git')))
