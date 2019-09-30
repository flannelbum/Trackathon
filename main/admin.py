from django.contrib import admin
from .models import Pledge, Station, Campaign, TATSetting, Goal, GivingLevel, GiftOption, GiftFulfillment

admin.site.site_header = 'Track-a-Thon Administration'
admin.site.register(Goal)
admin.site.register(Pledge)
admin.site.register(GivingLevel)
admin.site.register(GiftOption)
admin.site.register(GiftFulfillment)
admin.site.register(Station)
admin.site.register(Campaign)
admin.site.register(TATSetting)