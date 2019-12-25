################################################################################
#Importing libraries
################################################################################
from sense_hat import SenseHat
from datetime import datetime
import time
import RPi.GPIO as GPIO
from flask import Flask, render_template
from flask_mail import Mail, Message
from flask import send_file
import sys
global flag #global variable to check if the irrigation is on or off
################################################################################
#Defining some constants and declaring variables
################################################################################
r = 255 #red
g = 255 # green
b = 255 #blue
app = Flask(__name__) #flask instance
sense = SenseHat() #SneseHat instance
#configuration the email server
app.config['MAIL_SERVER']='smtp.gmail.com' #Email server "Gmail server"
app.config['MAIL_PORT'] = 587 #Email port "Common port by gmail"
app.config['MAIL_USERNAME'] = 'coe410project@gmail.com' #Gmail account created by us
app.config['MAIL_PASSWORD'] = 'COEcoe410!' #Gmail account password
app.config['MAIL_USE_TLS'] = True #Less safe connection so it is possible to send emails according to gmail
app.config['MAIL_USE_SSL'] = False #High safe connection but email cannot be send with its own

mail=Mail(app) #Mail instance
################################################################################
'''
LED fading function is to fade the led matrix depending on the number of the columns
that passed by the irrigation system function based on the case of the weather
'''
################################################################################
def LED_Fading(NumOfCol):
    if NumOfCol == 1:
        for i in range(8):
            for j in range(8):
                sense.set_pixel(i, j, r, g, b) #set pixel function which takes 5 parameters
                #i which is x coordinate, j as y coordinate, r for red, g for green, b for blue
            time.sleep(0.1)
            sense.clear()
    elif NumOfCol == 3:
        for i in range(8):
            for j in range(8):
                sense.set_pixel(i, j, r, g, b)
                if i > 5: #Because we are increment by 1 so we need to break when i reaches 7
                  break
                sense.set_pixel(i + 1, j, r, g, b)
                if i > 5:
                  break
                sense.set_pixel(i + 2 , j, r, g, b)
            time.sleep(0.1)
            for j in range(8):
              sense.set_pixel(i, j, 0, 0, 0)
            #sense.clear()
    elif NumOfCol == 5:
      for i in range(8):
            for j in range(8):
                sense.set_pixel(i, j, r, g, b)
                if i > 3:
                  break
                sense.set_pixel(i + 1, j, r, g, b)
                if i > 3:
                  break
                sense.set_pixel(i + 2 , j, r, g, b)
                if i > 3:
                  break
                sense.set_pixel(i + 3 , j, r, g, b)
                if i > 3:
                  break
                sense.set_pixel(i + 4, j, r, g, b)
            time.sleep(0.1)
            for j in range(8):
              sense.set_pixel(i, j, 0, 0, 0) 
    elif NumOfCol == 7:
      for i in range(8):
            for j in range(8):
                sense.set_pixel(i, j, r, g, b)
                if i > 2:
                  break
                sense.set_pixel(i + 1, j, r, g, b)
                if i > 2:
                  break
                sense.set_pixel(i + 2 , j, r, g, b)
                if i > 2:
                  break
                sense.set_pixel(i + 3 , j, r, g, b)
                if i > 2:
                  break
                sense.set_pixel(i + 4, j, r, g, b)
                if i > 2:
                  break
                sense.set_pixel(i + 5, j, r, g, b)
                if i > 1:
                  break
                sense.set_pixel(i + 6, j, r, g, b)
            time.sleep(0.1)
            for j in range(8):
              sense.set_pixel(i, j, 0, 0, 0)  
    else:
      return "Error, wrong number of columns"


################################################################################
'''
Irrigation system function has many cases to check on the temperature and humditiy 
#and turn it on or off correspondingly
It also set the case to specific number to send it to LED_Fading function to 
switch the leds on
'''
################################################################################
def Irrigation_System():
    case = 0
    humidity = round(sense.get_humidity())
    temperature = round(sense.get_temperature())
    if humidity > 10.0 and humidity <= 20.0 and temperature > 10.0 and temperature < 20.0:
        case = 1
        flag = True
    elif humidity > 20.0 and humidity <= 30.0 and temperature > 20.0 and temperature < 30.0:
        case = 3
        flag = True
    elif humidity > 30.0 and humidity <= 40.0 and temperature > 30.0 and temperature < 40.0:
        case = 5
        flag = True
    elif humidity > 40.0 and humidity <= 50.0 and temperature > 40.0 and temperature < 50.0:
        case = 7
        flag = True
    else:
        flag = False
    return case

################################################################################
'''
Home route of flask server, it renders a template with title and send it to
home.html page
'''
################################################################################
@app.route('/')
def root():
    templateData = {
        'title' : 'Home page',
    }
    return render_template('home.html', **templateData)

################################################################################
'''
Send email route is to send an email based on the entered email from the user
through the email that configured above, and it also renders a template with 
title of the page and the recipient email and send them to email.html page
'''
################################################################################
@app.route("/Send_Email/<recEmail>")
def SendEmail(recEmail):
    temp = round(sense.get_temperature(), 2) #get the temperature
    humidity = round(sense.get_humidity()) #get the humditiy
    #Message function has 3 parameters with title of the email first then sender and recipient email
    msg = Message('Irrigation System Report', sender = 'coe410project@gmail.com', recipients = [recEmail])
    localTime = time.ctime()
    #the body of the message
    msg.body = "%s\nTemperature is: %f\nThe Humidity is: %f\nThe Pressure is: %f" %(localTime, temp, humidity, Pressure)
    mail.send(msg) #And then send the message
    templateData = {
        'title' : 'Irrigation Email System',
        'email' : recEmail
    }
    return render_template('email.html', **templateData)

################################################################################
'''
Weather route is to show the weather status and return a template that has all
variables and it also renders a template with title of the page, temperature,
humidity and Pressure and send it to the weather.html page
'''
################################################################################
@app.route('/weather')
def Weather():
    temp = round(sense.get_temperature(), 2)
    humidity = round(sense.get_humidity())
    Pressure = round(sense.get_pressure())
    templateData = {
      'title' : 'Weather System',
      'temp': temp,
      'humidity': humidity,
      'pressure': Pressure
    }
    return render_template('weather.html', **templateData)

################################################################################
'''
Irrigation route with status on or off to turn on or off the irrigation
system based on the previous status of the system and it also renders a template with 
title of the page and status of the irrigation system and send it to 
the irrigation.html page
'''
################################################################################
@app.route('/irrigation/<Status>')
def Irrigation(Status):
    flag = Irrigation_System()
    if Status == "ON":
        if flag:
            templateData = {
                'title' : 'Irrigation System',
                'status' : 'The irriagtion system is already ON',
            }
            case = Irrigation_System()
            LED_Fading(case)
        else:
            flag = True
            templateData = {
                'title' : 'Irrigation System',
                'status' : 'The irriagtion system now is ON',
            }
            case = Irrigation_System()
            LED_Fading(case)
    elif Status == "OFF":
        if flag:
            flag = False
            templateData = {
                'title' : 'Irrigation System',
                'status' : 'The irriagtion system now is OFF',
            }
            sense.show_message("OFF")
        else:
            templateData = {
                'title' : 'Irrigation System',
                'status' : 'The irriagtion system already is OFF',
            }
            sense.show_message("OFF")
    else:
        return "Error, Wrong input!"
    return render_template('irrigation.html', **templateData)

################################################################################
'''
The system is controlled by the joystick on the SenseHat, so if the user move
it to the right, it will go to the weather station and it is also controlled
by the joystcik.
If the user move it to the left, the flask server will run.
'''
################################################################################
while True:
    sense.clear()
    print "\t\t\tWelcome to Irrigation System"
    time.sleep(0.5)
    print "To control the system, Use the joystick"
    time.sleep(0.5)
    print "Weather (right), irrigation remotely (left)"
    event = sense.stick.wait_for_event()
    time.sleep(1)
    if event.direction == "right": #Weather case
        print "Weather System"
        while True:
            print "Temp(up), Humidity(down), Pressure(left), Status(right)"
            event = sense.stick.wait_for_event(emptybuffer=True)
            # Check if the joystick was pressed
            if event.action == "pressed": #Checking if the joystick is pressed first
                if event.direction == "middle": #if middle is to exit the system
                    print "\t\t\tThank you for using the system"
                    sys.exit()
                elif event.direction == "up": #if up show the temperature on the terminal and led matrix
                    temp = round(sense.get_temperature(), 2)
                    print "Temperature is: %f" %(temp)
                    sense.show_message(str(temp))
                elif event.direction == "down":#if down show the humditiy on the terminal and led matrix
                    humidity = round(sense.get_humidity())
                    print "Humidity is: %f" %(humidity)
                    sense.show_message(str(humidity))
                elif event.direction == "left":#if left show the pressure on the terminal and led matrix
                    Pressure = round(sense.get_pressure())
                    print "Pressure is: %f" %(Pressure)
                    sense.show_message(str(Pressure))
                elif event.direction == "right":#if right show the status of irrigation system on the terminal and led matrix
                    if Irrigation_System:
                        print "Irrigation is ON"
                        case = Irrigation_System()#check whcih case of the irrigation system status
                        LED_Fading(case)#and then pass it led fading
                    else:
                        print "Irrigation is OFF"
                        sense.show_message("OFF")
    elif event.direction == "left":
         if __name__ == "__main__":
            app.run(host='0.0.0.0', port= 2323)
            #app.run(host='192.168.1.140',port=5060)#run the server on the host
