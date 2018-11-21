#!/usr/bin/python
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import shutil, time, json, string, cgi, subprocess, json, PIL, cv2, subprocess, colorutils, pprint, os
import picamera
from datetime import datetime
import numpy as np
import settings as settings
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from operator import itemgetter
        
# begin the attempt to get the current weather for sunrise data (get what time the sunrises)
count = 0
timeNow = int(time.time())
font = ImageFont.truetype("/home/pi/WakeUpMirror/fonts/BitstreamVeraSans.ttf", 16)
fontSmall = ImageFont.truetype("/home/pi/WakeUpMirror/fonts/BitstreamVeraSans.ttf", 14)
pp = pprint.PrettyPrinter(indent=4)

# get camera resource, keep trying if the other script is using it
while True:
    try:
        camera = picamera.PiCamera()
        camera.vflip = False
        camera.hflip = False
        break
    except (Exception):
        time.sleep(10)

# current weather values
weatherInfo = None
sunriseTime = ''
currentFeelsLikeTemp = ''
currentHumidity = ''
currentSummary = ''
currentWindSpeed = ''
currentCloudCover = ''
todayFeelsLikeTempHigh = ''
todayFeelsLikeTempLow = ''
todaySummary = ''

#-----------------------------------------------------------------------------------------------------------------------------
# get the temp and conditions at sunrise and conditions for the day (try 10 times in case of network outage other errors)
#-----------------------------------------------------------------------------------------------------------------------------
while count < 10:
    try:
        count = count + 1
        weatherInfo = json.loads(subprocess.check_output(['curl', settings.weatherAPIURL]))        
        sunriseTime = weatherInfo['daily']['data'][0]['sunriseTime']
        currentFeelsLikeTemp = weatherInfo['currently']['apparentTemperature']
        currentHumidity = weatherInfo['currently']['humidity']
        currentSummary = weatherInfo['currently']['summary']
        currentWindSpeed = weatherInfo['currently']['windSpeed']
        currentCloudCover = weatherInfo['currently']['cloudCover']
        todayFeelsLikeTempHigh = weatherInfo['daily']['data'][0]['temperatureMax']
        todayFeelsLikeTempLow = weatherInfo['daily']['data'][0]['temperatureMin']
        todaySummary = weatherInfo['hourly']['summary']
        break
    except (Exception):
        time.sleep(10)

#-----------------------------------------------------------------------------------------------------------------------------
# sleep till sunrise, then start capturing pictures, if no times found then just sleep for 2 hours (so roughly around 6am)
#-----------------------------------------------------------------------------------------------------------------------------

#set back 30 minutes to get the best colors
sunriseTime = sunriseTime - 1800
timeTillSunrise = sunriseTime - timeNow
if (timeTillSunrise > 0):
    print "Sleeping till Sunrise (zzz): " + str(timeTillSunrise) + " seconds"
    time.sleep(timeTillSunrise)
else:
    time.sleep(1)

#-----------------------------------------------------------------------------------------------------------------------------
# take set number of pictures in the desired time frame after sunset (set in settings)
#-----------------------------------------------------------------------------------------------------------------------------
colorsInPictures = {}
pictureColorTotals = {}
cameraPictureTaken = settings.projectFolder + 'image.jpg'
secondsBetweenPictures = int((settings.timeToCaptureMinutes * 60) / settings.numberOfSunriseCaptures)
sunriseOccuredTime = datetime.fromtimestamp(sunriseTime)
sunriseOccuredTime = sunriseOccuredTime.strftime('%l:%M%p on %b %d %Y')
while count <= settings.numberOfSunriseCaptures:
    try:

        # capture image from camera
        camera.capture(cameraPictureTaken)

        # save the current capture
        pictureTakenFileName = time.strftime('%l:%M%p on %b %d %Y').replace(" ", "-")
        pictureTakenFileName = 'Sunrise-' + pictureTakenFileName + '.jpg';
        pictureTaken = time.strftime('%l:%M%p on %b %d ')
        subprocess.call(['cp', cameraPictureTaken, settings.projectFolder + '/sunrise-pictures/' + pictureTakenFileName ])
        colorsInPictures[pictureTakenFileName] = {}
        pictureColorTotals[pictureTakenFileName] = 0

        pictureColorTotals[pictureTakenFileName] = len(colorsInPictures[pictureTakenFileName])
        time.sleep(secondsBetweenPictures)
        count = count + 1
        
    except (Exception):
       time.sleep(secondsBetweenPictures)

# get the most colorful image and display it on the digole display / email it to user for morning email
mostColorfulImage = ''
for key, value in sorted(pictureColorTotals.iteritems(), key=lambda (k,v): (v,k)):
    mostColorfulImage = key
mostColorfulImage = settings.projectFolder + '/sunrise-pictures/' + mostColorfulImage
print 'Most Colorful Sunrise Image is: ' + mostColorfulImage

# draw the current conditions and time on the sunrise full image
img = Image.open(mostColorfulImage)
draw = ImageDraw.Draw(img)
try:
    imageCurrentlyText = 'Sunrise Conditions @ [' + str(sunriseOccuredTime) + ' ] / ' + str(currentSummary) + ' / Felt Like: ' + str(int(currentFeelsLikeTemp)) + '*F [' + str(int(currentHumidity*100)) + '%]'
    imageCurrentlyText2 = 'Wind Speed was: ' + str(int(currentWindSpeed)) + ' mph / Cloud Cover was: ' + str(int(currentCloudCover*100)) + '%' 
    imageForecastText = 'Today\'s Forecast: High (' + str(int(todayFeelsLikeTempHigh)) + '*F) / Low (' + str(int(todayFeelsLikeTempLow)) + '*F) / ' + str(todaySummary)
except:
    imageCurrentlyText = ''
    imageCurrentlyText2 = ''
    imageForecastText = ''

draw.text( (10, 400), imageCurrentlyText , (255,255,200), font=font )
draw.text( (10, 425), imageCurrentlyText2 , (255,255,200), font=font )
draw.text( (10, 450), imageForecastText , (200,200,200), font=fontSmall )
img.save(mostColorfulImage)

# get the current most colorful to move over to the webserver and email it
shutil.move(mostColorfulImage, 'mostColorful.jpg')

# email the most colorful image as a morning email
subprocess.Popen( "/usr/bin/uuencode mostColorful.jpg sunrise.jpg | /usr/bin/mail -s 'Sunrise: " + time.strftime('%b %d, %Y') +"' " + settings.emailAddress, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# upload the image to the webhost to show on sunrise mirror
subprocess.Popen( "sshpass -p '" + settings.sftpPass + "' scp -o 'StrictHostKeyChecking no' mostColorful.jpg " + settings.sftpUser + "@" + settings.sftpHost + ":" + settings.sftpFolder, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

