#N&#x014d;tifs notifier demo

N&#x014d;tifs (short for notifications) provides a method for users to receive opt-in notifications from services of their choice. Examples of such services (notifiers) include emergency alerts, messages from personal devices like alarm systems, news alerts, newsletters, and advertising. A more complete description of N&#x014d;tifs can be found [here](https://altmode.org/notifs).

notif-notifier is a Python library for creating, sending, updating, and deleting N&#x014d;tifs. It works in conjunction with the recipients' notification agents, an example implementation of which is in the notif-agent and notif-management repositories. An example application, "clockwatcher", is also included which generates a n&#x014d;tif once a minute and sends it to a list of recipients once a minute. Recipients can subscribe to clockwatcher n&#x014d;tifs through a Web interface, and unsubscribe via their notification agent.

##notify.py Library

`notify.py` is the library itself. It requires the `Crypto.PublicKey.RSA` library to cryptographically sign n&#x014d;tifs; one way this library can be installed is via the command `pip install pycrypto`.

In order to sign n&#x014d;tifs, a DKIM-compatible keypair needs to be generated and the public key published in the notifer domain's DNS. A good way to do this is with the opendkim-genkey command that is included as part of the opendkim package, which is installable from popular Linux distributions or as described on the [opendkim website](http://opendkim.org/). The .txt file generated, containing the public key, needs to be added to your domain's DNS records; how this is done depends on your DNS provider. The .private file, containing the private key, needs to be protected and the file's name is the is loaded when a Signer object is created, normally when the notifying program starts. The selector name is arbitrary but needs to match the name given to the public key record in DNS.

##clockwatcherd.py example

`clockwatcherd.py` is a simple example application that generates notifications once a minute. By default it attempts to daemonize itself, but this can be disabled (for testing, etc.) by uncommenting two indicated lines near the bottom of the program.

The `daemon` library it uses is the one described [here](http://pypi.python.org/pypi/python-daemon). Note that there are other packages called `daemon` around so if Python complains about not having a DaemonContext class, you probably have the wrong one. The right one is installed as the python-daemon package by aptitude on Debian.  For daemonizing, it's a good idea if all of the files are given absolute pathnames.

##Clockwatcher authorization

A simple Web application is included to allow users to subscribe to Clockwatcher notifications and more generally to illustrate how to allow users to subscribe to notifications.

The Web application consists of the following:

* `clockwatcher.html` - Web page that explains what Clockwatcher does and prompts the user to authorize notifications
* `saveauth.py` - Python program that saves the authorization address for use by the clockwatcherd daemon
* `rihard-Clock-Calendar-1.png` - The clock image used on the page, courtesy of [Openclipart](https://openclipart.org)

The Clockwatcher Web application also uses the [Zurb Foundation CSS package](http://foundation.zurb.com/docs/css.html).

You will need to customize the clockwatcher.html file, substituting the name of your domain for `example.net` and supplying the correct URL for the callback.

##Installation

The clockwatcher authorization website is installed in a standard manner, with `clockwatcher.html` and the clock image going into (usually) `/var/www/html` or a subdirectory of it, and saveauth.py going into a directory for executables such as `/var/www/cgi-bin`. Install the Zurb Foundation CSS files in the `css` subdirectory of that directory. It may be helpful to rename `clockwatcher.html` to `index.html` so it is accessed by default.

`saveauth.py` needs write access to `/etc/newwatchers.cfg` in order to pass new notification addresses to the running clockwatcherd daemon. This isn't a very elegant form of interprocess communication, but it works for now.

It may also be necessary to modify the web server configuration file, depending on the server being used and the form of the installation.

`clockwatcherd.py` and `notify.py` should be installed in the same directory and be made executable. In order to daemonize itself, it needs to run as root; alternatively, you may uncomment the indicated lines near the bottom of `clockwatcherd.py` to inhibit daemonization use a command such as `nohup clockwatcherd.py &` to invoke the program.

##Clockwatcher demo

Rather than running clockwatcher yourself, you can also test a running N&#x014d;tifs agent by registering for n&#x014d;tifs at [http://clock.bluepopcorn.net](http://clock.bluepopcorn.net). 

