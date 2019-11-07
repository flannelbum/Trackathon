from django.contrib import admin
from .models import Pledge, Station, Campaign, TATSetting, Goal, GivingLevel, GiftOption, GiftAttribute, Gift

admin.site.site_header = 'Track-a-Thon Administration'
admin.site.register(Goal)
admin.site.register(Pledge)
admin.site.register(GivingLevel)
admin.site.register(GiftOption)
admin.site.register(GiftAttribute)
admin.site.register(Gift)
admin.site.register(Station)
admin.site.register(Campaign)
admin.site.register(TATSetting)