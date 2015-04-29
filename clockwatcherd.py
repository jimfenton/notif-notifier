#!/usr/bin/python

# clockwatcherd.py - Daemon to generate test notifs once a minute
#
# Copyright (c) 2015 Jim Fenton
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

__version__="0.1.0"

import sys
import traceback
from datetime import timedelta, datetime, date, time
import time
import daemon
import syslog
import signal
import lockfile
from notify import Signer, Notification
        
def clockwatcher_main():

    syslog.syslog("clockwatcherd: starting clockwatcher_main")

    lifetime = timedelta(days=1) #Notif expiration delta

    s = Signer("/etc/clockwatcher/shiny.private", "shiny")

    addrlist=[]
    updates={}
    with open("/etc/clockwatcher/clockwatcherd.cfg","r") as cfg:
        for line in cfg:
            addrlist.append(line[:-1])  #remembering to remove trailing \n

    while 1:

        # Synchronize to next whole minute
        starttime = time.localtime()
        time.sleep(60-starttime.tm_sec)

        currtime = datetime.now()+ timedelta(seconds=30) # Force rounding in case we're early
        timemsg = currtime.strftime("It is now %H:%M")
        

        notif = Notification(4, lifetime, timemsg, timemsg + " and all is well") # Need to add expiration here
        notif.prepare(s)

# For now, minimizing the possibility of a collision between this daemon and new authorizations coming in
# by reading the additional authorizations from a separate file and adding them on here. Only the daemon
# touches the main clockwatcherd.cfg file.

        rewrite = False
        try:
            with open("/etc/clockwatcher/newwatchers.cfg","r") as cfg:
                for line in cfg:
                    newaddr = line
                    if newaddr not in addrlist:  #Handle unlikely duplicates
                        addrlist.append(newaddr)
                        rewrite = True
        except IOError:
            pass
        except:
            syslog.syslog("clockwatcherd: Unknown error opening newwatchers file")
            quit()

        if rewrite:
            cfg=open("/etc/clockwatcher/newwatchers.cfg","w")  #Clobber newwatchers file
            cfg.close()

            with open("/etc/clockwatcher/clockwatcherd.cfg","w") as cfg: #Update config with new watchers
                for idx in range(len(addrlist)):
                    if addrlist[idx] != "":
                        cfg.write(addrlist[idx])
                        cfg.write("\n")
            rewrite = False

        for idx in range(len(addrlist)):
            notaddr = addrlist[idx]
            if notaddr == "":
                continue
            if notaddr in updates:  #update an existing notif if possible
                notid = updates[notaddr]
                status = notif.update(notid)
                if status == 404: #if 404 delete notid from updates
                    del updates[notaddr]
            if notaddr not in updates:  #not an else because it could have just been removed

                # TODO: Handle exceptions (can't connect, etc.) here
                (notid, status) = notif.send(notaddr) #Need to get feedback on send failures, delete notaddr
                if status == 404:
                    addrlist[idx]=""   #Don't delete entry from addrlist inside loop, just blank it
                    rewrite = True  #Disk copy of list needs updating
                elif status == 200:
                    updates[notaddr] = notid

        if rewrite:  #Update disk copy of list, removing any blank addresses
            with open("/etc/clockwatcher/clockwatcherd.cfg","w") as cfg:
                for idx in range(len(addrlist)):
                    if addrlist[idx] != "":
                        cfg.write(addrlist[idx])
                        cfg.write("\n")

                        
def program_cleanup():
    conn.close()
    syslog.syslog("clockwatcherd: exiting on signal")
    quit()

# Uncomment next 2 lines for non-daemon testing 
#clockwatcher_main()
#quit()

context = daemon.DaemonContext(
    pidfile=lockfile.FileLock('/var/run/clockwatcherd.pid'),
    )

context.signal_map = {
    signal.SIGHUP: program_cleanup,
    }

with context:
    clockwatcher_main()
