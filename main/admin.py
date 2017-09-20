from django.contrib import admin

from .models import Pledge, TrackathonSetting, Station
admin.site.register(Pledge)
admin.site.register(TrackathonSetting)
admin.site.register(Station)