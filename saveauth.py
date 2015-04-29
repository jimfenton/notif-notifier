#!/usr/bin/python

# saveauth.py - Save notif address for use by clockwatcherd
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

import cgi

print """Content-Type: text/html

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html>
<head>
  <title>Clockwatcher</title>
</head>
<body>
"""

form = cgi.FieldStorage()
if "addr" not in form:
    print "<h1>Error</h1>"
    print "Authorization ID not present"
    exit()

if "maxpri" not in form:
    print "<h1>Error</h1>"
    print "Max priority not present"
    exit()

with open("/etc/clockwatcher/newwatchers.cfg", "a") as config:
    config.write(form["addr"].value)
print "<h1>N&#x014d;tif authorized</h1>"
print "<p>"
print "Have a good time!"
print "</p>"
print "</body></html>"

