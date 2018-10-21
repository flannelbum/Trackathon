from django.contrib import admin
from .models import Pledge, Station, Campaign

admin.site.site_header = 'Track-a-Thon Administration'
admin.site.register(Pledge)
admin.site.register(Station)
admin.site.register(Campaign)