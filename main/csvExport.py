import csv
import time

from django.http.response import HttpResponse

from main.models import Pledge
from trackathon import settings


def csvExport(request):

    cfgpw = request.POST.get('cfgpw')
    # print(cfgpw)

    if cfgpw == settings.CONFIG_PASSWORD:
        filename = "TrackAThonExport_" + time.strftime("%m%d-%H%M%S") + ".csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'DATEADDED', 'AMOUNT', 'FIRSTNAME', 'LASTNAME', 'CITY', 'FTD', 'PLEDGETYPE', 'STATION', 'PARISH', 'CALLOUT', 'COMMENT'])
        
        entries = Pledge.objects.all()
        for entry in entries:
            # writer.writerow([ entry.id, entry.create_date.strftime("%Y-%m-%d %H:%m:%S"), entry.amount, entry.firstname, entry.lastname, entry.city, entry.ftdonor, entry.singleormonthly, entry.callsign, entry.parish, entry.groupcallout, entry.comment])
            # # fix up the hour string for -4
            myhour = entry.create_date.strftime("%H")
            myhour = +int(myhour) - 4
            timestr = entry.create_date.strftime("%Y/%m/%d ") + str(myhour) + ":" + entry.create_date.strftime("%M:%S")
            writer.writerow([ entry.id, timestr, entry.amount, entry.firstname, entry.lastname, entry.city, entry.ftdonor, entry.singleormonthly, entry.callsign, entry.parish, entry.groupcallout, entry.comment])
    else:
    # Return silent/404 if blank GET request
        return HttpResponse(status=404)
    
    return response
    writer = csv.writer(response)
    writer.writerow(['ID','DATEADDED','AMOUNT','FIRSTNAME','LASTNAME','CITY','FTD','PLEDGETYPE','STATION','PARISH','CALLOUT','COMMENT'])
    
    entries = Pledge.objects.all()
    for entry in entries:
        # writer.writerow([ entry.id, entry.create_date.strftime("%Y-%m-%d %H:%m:%S"), entry.amount, entry.firstname, entry.lastname, entry.city, entry.ftdonor, entry.singleormonthly, entry.callsign, entry.parish, entry.groupcallout, entry.comment])
        ## fix up the hour string for -4
        myhour = entry.create_date.strftime("%H")
        myhour =+ int(myhour) - 4
        timestr = entry.create_date.strftime("%Y/%m/%d ") + str(myhour) + ":" + entry.create_date.strftime("%M:%S")
        writer.writerow([ entry.id, timestr, entry.amount, entry.firstname, entry.lastname, entry.city, entry.ftdonor, entry.singleormonthly, entry.callsign, entry.parish, entry.groupcallout, entry.comment])
    else:
        # Return silent/404 if blank GET request
        return HttpResponse(status=404)
    
    return response