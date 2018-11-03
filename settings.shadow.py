#!/usr/bin/python
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0

# your email address (sunrise pictures mailed out)
emailAddress = 'me@gmail.com'

# forecast.io API key for local weather information
weatherAPIURL = 'https://api.forecast.io/forecast/'
weatherAPIKey = 'MY API KEY HERE'

# digole display driver settings
projectFolder = '/home/pi/WakeUpMirror/'

# capture image settings
basewidth = 160
hsize = 128

# number of sunrise images to capture in the morning
numberOfSunriseCaptures = 15

# how long after sunrise to capture pictures for in minutes
timeToCaptureMinutes = 30

# search google to get the Latitude/Longitude for your home location
latitude = 45
longitude = -72

# SFTP upload connection
sftpHost = 'mywebsite.com'
sftpFolder = '/var/www/path/to/webroot'
sftpUser = 'username'
sftpPass = 'password'
