'''
Created on Apr 26, 2012

@author: Nader
'''
try:
    from django.template.loader import render_to_string
except ImportError:
    pass
import requests
import datetime
import time, random
from time import strftime
from pom.bldg_info import *


url_alt = 'http://laundryview.com/lvs.php'
#url_stub is the base url to get the laundry data for the rooms.
#url_stub+roomid gives the data for a specific room with id=roomid
url_stub = 'http://classic.laundryview.com/laundry_room.php?view=c&lr='
bldg_id_to_laundry_info = {
    'BLOOM' : (('Bloomberg 269', '3073440'), ('Bloomberg 332', '3073441'), ('Bloomberg 460', '3073442'), ('Bloomberg 41', '3073427')), 
    'HARGH' : (('Whitman FB11', '3073469'), ('Whitman S201', '3073472'), ('Whitman C205', '3073466'), ('Whitman A119', '3073465'), ('Whitman C305', '3073467'), ('Whitman S301', '3073473'), ('Whitman C407', '3073468'), ('Whitman S401', '3073474'), ('Whitman F403', '3073471'), ('Whitman F312', '3073470')), 
    'SCULL' : (('Scully South Wing - Fourth Floor', '3073420'), ('Scully South Wing - First Floor', '3073419'), ('Scully North Wing - Second Floor', '3073418')), 
    'PATTN' : (('Patton Hall Basement Level', '3073416'), ('Patton Hall Fourth Floor', '3073416')), 
    'PYNEH' : (('Pyne', '3073417'),), 
    'HAMIL' : (('Hamilton', '3073443'),), 
    'JOLIN' : (('Joline', '3073411'),), 
    'LOCKH' : (('Lockhart', '3073428'),), 
    'LITTL' : (('Little Hall B6', '3073464'), ('Little Hall A49', '3073426'), ('Little Hall Basement Level A5', '3073413')), 
    'EDWAR' : (('Edwards', '307345'),), 
    'FEINB' : (('Feinburg', '307346'),), 
    'BLAIR' : (('Blair', '307342'), ('Buyers', '3073444')), 
    'CLAPP' : (('Clapp - 1927', '307343'),), 
    'DODHA' : (('Dod', '307344'),), 
    'BROWN' : (('Brown', '3073475'),), 
    'WITHR' : (('Witherspoon', '3073422'),), 
    'LAUGH' : (('Laughlin Hall', '3073412'),), 
    'C1915' : (('1915', '3073424'),), 
    'HENRY' : (('Henry', '3073410'),), 
    'FORBC' : (('Forbes Annex', '307348'), ('Forbes Main', '307347')), 
    'SPELM' : (('Spelman', '3073421'),), 
    'HOLDE' : (('Holder', '307349'),), 
    '1903H' : (('1903', '3073423'),), 
    '1976H' : (('1976', '3073462'),), 
    'YOSEL' : (('Yoseloff', '3073463'),)
}


class Room(object):
    def __init__(self, laundryurl):
        self._time = strftime("%Y-%m-%d %H:%M:%S")

        resp = requests.get(laundryurl)
        f = resp.content.split('\n')

        try:
            self._washers = []
            self._dryers = []
            for line in f:
                y = []
                if 'WASHERS' in line:
                    y = line.split()
                    i = y.index('of')
                    self._washers.append(y[i-1])
                    self._washers.append(y[i+1])
                if 'DRYERS' in line:
                    y = line.split()
                    i = y.index('of')
                    self._dryers.append(y[i-1])
                    self._dryers.append(y[i+1])
                    break
        except:
            raise Exception("couldn't parse the LaundryView page")

    def time(self):
        return self._time

    def washers(self):
        return self._washers

    def dryers(self):
        return self._dryers


def print_laundry_info(laundry_info):
    '''print the results as an example'''
    for name,info in laundry_info.iteritems():
        print(name + ' \n\twashers: ' + str(info.washers()[0]) + ' free of ' + str(info.washers()[1]) + ' \n\tdryers: ' + str(info.dryers()[0]) + ' free of ' + str(info.dryers()[1]))


####
# The following functions are common to all modules in pom.scrape
# We may want to put them in a class for OO-programming purposes
####

def get_bldgs():
    return tuple(bldg_id_to_laundry_info.keys())

def scrape():
    '''
    Cannot access this from dev server-- substituted with temporary
    values for demo. You can literally just uncomment the code below
    on a server with access to the laundry website and everything will work.
    '''

    timestamp = datetime.datetime.now()

    laundry_info = {}
    for id, info in bldg_id_to_laundry_info.iteritems():
        laundry = []
        for x in info:
            room_obj = Room(url_stub + x[1])
            # sleep so laundryview doesn't get suspicious
            time.sleep(random.random()/1)
            laundry.append((x[0], room_obj.washers()[0], room_obj.washers()[1], room_obj.dryers()[0], room_obj.dryers()[1]))
        laundry_info[id] = tuple(laundry)
    
    mapping = {}
    for building,rooms in laundry_info.items():
        rooms_list = list(rooms)
        for i in  range(0, len(rooms)):
            room = list(rooms_list[i])
            if (room[1] == '0'): #if no washers left
                room.append('#FF0000') #red
            else:
                room.append('#00AA00') #green
            if (room[3] == '0'): #if no dryers left
                room.append('#FF0000') #red
            else:
                room.append('#00AA00') #green
            rooms_list[i] = tuple(room)
        rooms_list = tuple(rooms_list)
        mapping[building] = rooms_list
    return (timestamp, mapping)


def render(scraped=None):
    if not scraped:
        scraped = scrape()
    timestamp, machine_mapping = scraped
    machine_list = []
    for bldg_code, machines in machine_mapping.iteritems():
        machines = sorted(machines, key=lambda x: x[0])
        machine_list.append((bldg_code, BLDG_INFO[bldg_code][0], machines))
    machine_list = sorted(machine_list, key=lambda x: x[1])
    html = render_to_string('pom/data_laundry.html',
                            {'machine_list' : machine_list})
    return {'timestamp': timestamp.strftime("%B %e, %l:%M %p"),
            'html': html}

