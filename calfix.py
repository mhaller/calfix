# CalFix v1
#
# The aim of the CalFix tool is to fix ICS/iCalendar data
# according to RFC 5545 (http://tools.ietf.org/html/rfc5545)
# as for instance exported from Google calendar, so that the 
# data can be imported to SabreDAV-based (http://code.google.com/p/sabredav/) 
# calendar software such as ownCloud (http://ownCloud.org) and
# can be synchronized flawlessly with CalDAV clients such as
# Apple iCal.     
#
# LICENSE GPLv3:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Copyright (c) 2013 Martin Haller <mail@martin-haller.net>
# 

import sys

# iCalendar module see http://www.kanzaki.com/docs/ical/
from icalendar import Calendar
from icalendar.tools import UIDGenerator 

yourDomain = 'yourDomain.org'

class CalFix:
    '''
    Copies only VEVENT and VTIMEZONE components, all other calendar 
    components are discarded (e.g. VALARM) and fixes VEVENTs
    
    Fixes for VEVENT
    - reassigns for each VEVENT a new UID as ...@yourdomain.org
    - fixes the LAST-MODIFIED item if it has the value 19700101T000000Z
    '''

    def __init__(self):
        self.uidDomain = 'defaultDomain.org'
        self.prodId = '-//CalFix Developer//NONSGML CalFix v1//EN';
    def _addPropIfAvailable(self, str, ie, oe):
        '''
        Looks for str in the input iCalendar event (ie) 
        and adds the value of str to the output iCalendar event (oe)
        if available and returns oe 
        '''
        prop = ie.get(str)
        if prop is not None and len(prop):
            oe.add(str, prop)
        return oe
    def fix(self, filename, uidDomain):
        '''
        Performs the actual fix of ICS calendar file
        
        @param     filename        ICS calendar file name without extension
        @param     uiDomain        domain name as used to create the UID  
        '''    
        if uidDomain is not None and len(uidDomain):
            self.uidDomain = uidDomain
        inCal = Calendar.from_ical(open(filename + '.ics','rb').read())
        uidGen = UIDGenerator()
        c = Calendar()
        c.name = 'VCALENDAR';
        c['version'] = '2.0'
        c['prodid'] = self.prodId
        c = self._addPropIfAvailable('X-WR-CALNAME',inCal,c)
        for ic in inCal.walk():
            if (ic.name == 'VTIMEZONE'):
                c.add_component(ic)
            if (ic.name != 'VEVENT'):
                continue
            e = ic
            # FIX-1: reassign a new UID to each VEVENT
            e['UID'] = uidGen.uid(self.uidDomain).to_ical()
            # FIX-2: set LAST-MODIFIED date to the date of creation 
            if e['LAST-MODIFIED'].to_ical() == '19700101T000000Z':
                e['LAST-MODIFIED'] = e['CREATED']
            c.add_component(e)
        with open(filename + '_calfix.ics', 'w') as icsOutFile:
            icsOutFile.write(c.to_ical())

if __name__ == '__main__':
    CalFix().fix(sys.argv[1], yourDomain)