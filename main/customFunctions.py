from datetime import datetime
from pytz import timezone

from random import choice, randint, sample

from django.conf import settings
from django.utils import lorem_ipsum

from main.forms import PledgeEntryForm
from main.models import Pledge, Station, GivingLevel
from tagging.models import Tag



def autotag(entry):
    # applies tags if the entry falls within a giving level
    for level in GivingLevel.objects.filter(campaign__exact=None):
        if entry.amount >= level.low_amount and entry.amount <= level.high_amount:
            tags = level.tag + ', '
            for tag in list(entry.tags.values_list('name', flat=True)):
                tags += tag + ', '
            entry.tags = tags
            entry.save()


def int_or_0(value):
    # Helper function to return an integer for a given value (string)
    #  if none found, return 0
    try:
        return int(value)
    except:
        return 0 


def getRandomPledgeForm():
    form = PledgeEntryForm()
    entry = generateRandomPledge(None, False)
    
    form.firstname = entry['firstname']
    form.lastname = entry['lastname']
    form.address1 = entry['address1']
    form.address2 = entry['address2']
    form.city = entry['city']
    form.state = entry['state']
    form.zip = entry['zip']
    form.is_anonymous = entry['is_anonymous']
    form.is_first_time_donor = entry['is_first_time_donor']
    form.is_monthly = entry['is_monthly']
    form.amount = entry['amount']
    form.station = entry['station']
    form.phone_number = entry['phone_number']
    form.tags = entry['tags']
    form.comment = entry['comment']
    
    return form

    
    
def generateRandomPledge(date, create_entry):
    
    if date == None:
        date = datetime.now()
    
    # Pool of values
    firstnames = ['John', 'Paul', 'George', 'Ringo', 'Christopher', 'David', 'Jane', 'Julia', 'Prudence', 'Cindy', 'Marge', 'Homer', 'Bart', 'Lisa', 'Maggie', 'Donna', 'Ron', 'Sean', 'Melanie', 'Colleen', 'Liam', 'Alan', 'Noel', 'Lilly', 'Mike', 'Terry', 'Jason', 'Jill', 'Tim']
    lastnames = ['Smith', 'Johnson', 'Davidson', 'Schwartz', 'Doe', 'Miller', 'Washington', 'Jefferson', 'Jones', 'Mayhew', 'Robertson', 'Dinkle', 'Westinghouse', 'Burns', 'Simpson', 'Harrison', 'Starr', 'McCartney', 'Lennon']
    streetnames = ['Glendale', 'Arlington', 'Detroit', 'Key', 'Greenvally', 'Oak', 'Ayers', 'Barrows', 'Pickle', 'Rugby']
    streettypes = ['Dr', 'Ave', 'Blvd', '']
    cities = ['Toledo', 'Perrysburg', 'Maumee', 'Port Clinton', 'Wallbridge', 'Sylvania', 'Holland', 'Swanton', 'Millbury', 'Rossford', 'Northwood', 'Lime City', 'Monclova', 'Genoa', ]
    states = ['OH', 'MI']
    
    try:   
        tags = ",".join(sample(list(Tag.objects.all().values_list('name', flat=True)),2))
    except(ValueError):
        print('Tag issue.  No tags in system?')
        tags = ''

    entrydict = {
        'create_date': date,
        'firstname': str(choice(firstnames)),
        'lastname': str(choice(lastnames)),
        'address1': str(choice(range(0,9999))) + " " + str(choice(streetnames)) + " " + str(choice(streettypes)),
        'address2': "",
        'city': str(choice(cities)),
        'state': str(choice(states)),
        'zip': str(choice(range(43000,43999))),
        'amount': randint(1,70),
        'is_anonymous': choice([True, False]),
        'is_first_time_donor': choice([True, False]),
        'is_monthly': choice([True, False]),
        'station': choice(Station.objects.all()),
        'phone_number': '(419)555-' + str(choice(range(0000,9999))),
        'tags': tags,
        }
    entrydict['comment'] = 'Randomly generated comment for ' + entrydict['firstname'] + ' ' + entrydict['lastname'] + ': ' + lorem_ipsum.words(randint(5,75), False)
    
    if create_entry:
        # Generate entry            
        entry = Pledge(
            create_date = entrydict['create_date'],
            firstname = entrydict['firstname'],
            lastname = entrydict['lastname'],
            address1 = entrydict['address1'],
            address2 = entrydict['address2'],
            city = entrydict['city'],
            state = entrydict['state'],
            zip = entrydict['zip'],
            amount = entrydict['amount'],
            is_anonymous = entrydict['is_anonymous'],
            is_first_time_donor = entrydict['is_first_time_donor'],
            is_monthly = entrydict['is_monthly'],
            station = entrydict['station'],
            phone_number = entrydict['phone_number'],
            comment = entrydict['comment']
            )
        # tags are special.  Have to have an entry before we can tag it.
        entry.save()
        entry.tags = tags
        entry.save()
        
    return entrydict
        
        
        
def generateDay(year, month, day, perHour=None):
    localtz = timezone( settings.TIME_ZONE)
    if perHour == None:
        for hour in range(5,20):
            for minute in range(0,60):
                generateRandomPledge(localtz.localize(datetime(year, month, day, hour, minute, 0)),True)
    else:
        for hour in range(5,13):
            for minute in range(0,perHour):
                generateRandomPledge(localtz.localize(datetime(year, month, day, hour, minute, 0)),True)



def prettydate(d):
    # http://stackoverflow.com/questions/410221/natural-relative-days-in-python
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(s/60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(s/3600)
    
    
import time
class Timer:
       
    def __init__(self):
        self.start = time.time()
    
    def elapsed(self):
        self.end = time.time()
        return str(self.end - self.start)
    
    
    
    

