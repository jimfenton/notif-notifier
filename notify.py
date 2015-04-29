#!/usr/bin/python
# notify.py - Library to generate and manage Notif notifications
#
# Copyright (c) 2014, 2015 Jim Fenton
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

import json
import jws
import requests
from datetime import datetime
import string
import hashlib
import base64
import Crypto.PublicKey.RSA as RSA
import sys



class Signer:

    def __init__(self, privkeyfile, selector):
        with open(privkeyfile, "r") as f:
            privkey=f.read()
        self.pk = RSA.importKey(privkey)
        self.selector = selector


class Notification:

    def __init__(self, priority, lifetime, subject, body):
        self.priority = priority # TODO: Ought to range check these
        self.lifetime = lifetime
        self.subject = subject
        self.body = body
        self.payload = None # Populated by prepare()
        self.signature = None # Populated by prepare()

    def prepare(self, signer):
        """Timestamp and sign a notif in preparation for sending, updating, etc.

        Argument:
        signer -- Signer object specifying the private key and selector to use
        """
        currtime = datetime.utcnow()
        self.expiration = datetime.isoformat(currtime + self.lifetime)+"Z"
        self.origtime = datetime.isoformat(currtime) + "Z"
        self.payload = json.dumps({"origtime": self.origtime,
                "priority": self.priority, "expires": self.expiration,
                "subject": self.subject, "body": self.body})
        self.protected = json.dumps({ 'alg':'RS256', 'kid':signer.selector })

        self.signature = jws.sign(self.protected, self.payload, signer.pk, True)

        return 0

    def send(self, to):
        """Send a signed notif

        Argument:
        to -- notif address including agent

        Returns:
        Notification ID including agent
        HTTP status code (200 for success, 404 if notification address unknown
        """
        if self.signature == None:
            raise ValueErr     #Probably needs prepare()
            
        url = IDtoURL(to)
        print "POST to ",url # DEBUG
        
        notifMsg = { "header": { "to": to },
                     "payload": base64.urlsafe_b64encode(self.protected).rstrip("=") + "." +
                     base64.urlsafe_b64encode(self.payload).rstrip("=") + "." + self.signature }
        try:
            r = requests.post(url, data=json.dumps(notifMsg))
        except:
            print "POST error to ", url, sys.exc_info()[0]
            return ("", 0)

        notID = None
        if r.status_code == 200:
            print r.text  # DEBUG
            rj = json.loads(r.text)
            notID = rj["notid"] + "@" + to[string.index(to, "@")+1:]
        
        return (notID, r.status_code)

    def _upddel(self, notid, delete=False):
        """Common tasks for update and delete methods"""
        if notid == None:
            raise ValueErr
        if self.signature == None:
            raise ValueErr        #Probably needs prepare()
        
        url = IDtoURL(notid)

        message = { "header": { "notid":notid },
                    "payload": base64.urlsafe_b64encode(self.protected).rstrip("=") + "." +
                    base64.urlsafe_b64encode(self.payload).rstrip("=") + "." + self.signature }

        if delete:
            print "DELE to ",url #DEBUG
            
            try:
                r = requests.delete(url, data=json.dumps(message))
                return r
            except:
                print "DELE error to ", url, sys.exc_info()[0]
                return None

        else:
            print "PUT to ",url #DEBUG
            try:
                r = requests.put(url, data=json.dumps(message))
                return r
            except:
                print "PUT error to ", url, sys.exc_info()[0]
                return None

            
    def update(self, notid):
        """Update a specified notif"""
        r = self._upddel(notid, False)
        if r == None:
            return 0
        return r.status_code
    
    def delete(self, notid):
        """Send a delete request for a specified notif"""
        r = self._upddel(notid, True)
        if r == None:
            return 0
        return r.status_code

def IDtoURL(id):
    """Convert an authorization or notification ID from address to URL format

    Example: "54DC1B81-1729-4396-BA15-AFE6B5068E32@example.org" becomes
             "http://example.org/notify/54DC1B81-1729-4396-BA15-AFE6B5068E32"
"""
    return "http://"+ id[string.index(id, "@")+1:] + "/notify/" + id[0:string.index(id, "@")] # TODO: Will need to change to https://

