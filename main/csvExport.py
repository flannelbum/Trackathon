import csv
import time

from django.http.response import HttpResponse
import pytz
from tagging.models import Tag

from main.models import Pledge
from main.views import decode_entries
from trackathon import settings


def csvExport(request):

    if request.user.is_authenticated:
        
        entries = decode_entries(request.GET.get('list'))
        bool(entries)
               
        filename = "TrackAThonExport_" + time.strftime("%m%d-%H%M%S") + ".csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        writer = csv.writer(response)
        
        csvheader = [
            'ID', 
            'DATEADDED', 
            'AMOUNT', 
            'FIRSTNAME', 
            'LASTNAME',
            'PHONE_NUMBER', 
            'CITY', 
            'STATION',
            'IS_THANKED',
            'IS_FIRST_TIME_DONOR',
            'IS_MONTHLY',
            ##'COMMENT',
            ]
        
        writer.writerow(csvheader)

        for pledge in entries:
            
            station = ''
            if pledge.station != None:
                station = pledge.station.callsign
            
            csvrow =[
                pledge.id, 
                pledge.create_date.astimezone( pytz.timezone( settings.TIME_ZONE )).strftime("%Y/%m/%d %H:%M:%S"), 
                pledge.amount, 
                pledge.firstname, 
                pledge.lastname,
                pledge.phone_number, 
                pledge.city, 
                station, 
                pledge.is_thanked,
                pledge.is_first_time_donor,
                pledge.is_monthly,
                ##pledge.comment,
                ]

            for tag in pledge.tags:
                csvrow.append(tag.name)
                
            writer.writerow(csvrow)
    else:
    # Return silent/404 if blank GET request
        return HttpResponse(status=404)
    
    return response