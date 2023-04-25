import sys
import os
from datetime import datetime
import time
from PIL import Image,ImageDraw,ImageFont
import requests
import board
import adafruit_dht
import RPi.GPIO as GPIO

BUTTON_PIN = 3
LED_PIN = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)


def button_callback(channel):
    global update_weather
    update_weather = True
    generate_output_image()
    
    write_to_screen(screen_output_file, 0)

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

update_weather = False

# Search lib folder for display driver modules
sys.path.append('library')
from waveshare_epd import epd7in5_V2
epd = epd7in5_V2.EPD()

dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'picture')
icondir = os.path.join(picdir, 'icon')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')


# define funciton for writing image and sleeping for 5 min.
def write_to_screen(image, sleep_seconds):
    print('Writing to screen.')
    # Write to screen
    h_image = Image.new('1', (epd.width, epd.height), 255)
    # Open the template
    screen_output_file = Image.open(os.path.join(picdir, image))
    # Initialize the drawing context with template as background
    h_image.paste(screen_output_file, (0, 0))
    epd.init()
    epd.display(epd.getbuffer(h_image))
    # Sleep
    time.sleep(2)
    epd.sleep()
    time.sleep(sleep_seconds)

# define function for displaying error
def display_error(error_source):
    # Display an error
    print('Error in the', error_source, 'request.')
    # Initialize drawing
    error_image = Image.new('1', (epd.width, epd.height), 255)
    # Initialize the drawing
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), error_source +' ERROR', font=font50, fill=black)
    draw.text((100, 300), 'Retrying in 30 seconds', font=font22, fill=black)
    current_time = datetime.now().strftime('%H:%M')
    draw.text((300, 365), 'Last Refresh: ' + str(current_time), font = font50, fill=black)
    # Save the error image
    error_image_file = 'error.png'
    error_image.save(os.path.join(picdir, error_image_file))
    # Close error image
    error_image.close()
    # Write error to screen 
    write_to_screen(error_image_file, 30)


def read_dht22_sensor1():
    try:
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        indoor_temp_str = "Indoor: {:.1f} F / {:.1f} C".format(temperature_f, temperature_c)
        indoor_humidity_str = "Humidity: {}%".format(humidity)

        return indoor_temp_str, indoor_humidity_str, temperature_c

    except RuntimeError as error:
        print(error.args[0])
        return None, None

    except Exception as error:
        dhtDevice.exit()
        raise error

    except KeyboardInterrupt:
        dhtDevice.exit()
        print('exiting script')

def read_dht22_sensor():
    try:
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        indoor_temp_str = "Temp: {:.1f}".format(temperature_c) + u'\N{DEGREE SIGN}C'
        indoor_humidity_str = "Hum: {}%".format(humidity)

        return indoor_temp_str, indoor_humidity_str, temperature_c

    except RuntimeError as error:
        print(error.args[0])
        return None, None, None

    except Exception as error:
        dhtDevice.exit()
        raise error

    except KeyboardInterrupt:
        dhtDevice.exit()
        print('exiting script')


def generate_output_image():
    global led_state_text
    global screen_output_file
    # Ensure there are no errors with connection
    error_connect = True
    while error_connect == True:
        try:
            # HTTP request
            print('Attempting to connect to OWM.')
            response = requests.get(URL)
            print('Connection to OWM successful.')
            error_connect = None
        except:
            # Call function to display connection error
            print('Connection error.')
            display_error('CONNECTION') 
    
    error = None
    while error == None:
        # Check status of code request
        if response.status_code == 200:
            print('Connection to Open Weather successful.')
            # get data in jason format
            data = response.json()
            
            # get current dict block
            current = data['current']
            # get current
            temp_current = current['temp']
            # get humidity
            humidity = current['humidity']
            # get pressure
            wind = current['wind_speed']
            # get description
            weather = current['weather']
            report = weather[0]['description']
            # get icon url
            icon_code = weather[0]['icon']
            #icon_URL = 'http://openweathermap.org/img/wn/'+ icon_code +'@4x.png'


            # get daily dict block
            daily = data['daily']
            # get min and max temp
            daily_temp = daily[0]['temp']
            temp_max = daily_temp['max']
            temp_min = daily_temp['min']
            sunrise_timestamp = daily[0]['sunrise']
            sunset_timestamp = daily[0]['sunset']
            sunrise_time = datetime.fromtimestamp(sunrise_timestamp).strftime('%I:%M %p')
            sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime('%I:%M %p')

            # Read indoor temperature and humidity
            indoor_temp_str, indoor_humidity_str, indoor_temp_c = read_dht22_sensor()
            # Control the LED based on the indoor temperature
            TEMP_THRESHOLD_C = 27  # Replace this with the desired temperature threshold in Celsius
            if indoor_temp_c and indoor_temp_c > TEMP_THRESHOLD_C:
                GPIO.output(LED_PIN, GPIO.HIGH)
                led_state_text = "AC: ON"
            else:
                GPIO.output(LED_PIN, GPIO.LOW)
                led_state_text = "AC: OFF"

                    
            # Set strings to be printed to screen
            string_location = LOCATION
            string_temp_current ='Currently: ' + format(temp_current, '.0f') + u'\N{DEGREE SIGN}C'
            string_humidity = 'Humidity: ' + str(humidity) + '%'
            string_wind = 'Wind: ' + format(wind, '.1f') + ' MPH(or Km/Hr)'
            string_report = 'Now: ' + report.title()
            string_temp_max = 'High: ' + format(temp_max, '>.0f') + u'\N{DEGREE SIGN}C'
            string_temp_min = 'Low:  ' + format(temp_min, '>.0f') + u'\N{DEGREE SIGN}C'
            
            
            # Set error code to false
            error = False
            
        else:
            # Call function to display HTTP error
            display_error('HTTP')

    # Open template file
    template = Image.open(os.path.join(picdir, 'template.png'))
    # Initialize the drawing context with template as background
    draw = ImageDraw.Draw(template)
    
    # Draw top left box
    ## Open icon file
    icon_file = icon_code + '.png' 
    icon_image = Image.open(os.path.join(icondir, icon_file))
    
    ## Resize the icon
    icon_width, icon_height = icon_image.size

    new_icon_width = icon_width // 2
    new_icon_height = icon_height // 2

    icon_image_resized = icon_image.resize((new_icon_width, new_icon_height), Image.ANTIALIAS)

    ### Paste the image
    template.paste(icon_image_resized, (40, 250))
    #current_time = datetime.now().strftime('%H:%M')
    current_time = datetime.now().strftime('%I:%M %p')  # Add %p for AM/PM
    current_date = datetime.now().strftime('%A, %B %d')  # Add date and day of the week

    draw.text((48, 51), current_time, font = font60, fill=black)
    draw.text((48, 148), current_date, font = font22, fill=black)
    ## Draw text
    draw.text((48, 200), string_report, font=font22, fill=black)
    # Draw top right box
    draw.text((472, 129), string_temp_current, font=font18, fill=white)
    # Draw bottom left box
    draw.text((472, 154), string_temp_max, font=font18, fill=white)
    #draw.rectangle((170, 385, 265, 387), fill=black)
    draw.text((472, 178), string_temp_min, font=font18, fill=white)
    # Draw bottom middle box
    draw.text((30, 380), string_humidity, font=font22, fill=black)
    draw.text((30, 418), string_wind, font=font22, fill=black)
    draw.text((610, 129), 'Sunrise: ' + sunrise_time, font=font18, fill=white)
    draw.text((610, 154), 'Sunset: ' + sunset_time, font=font18, fill=white)
    draw.text((630, 303), led_state_text, font=font18, fill=black)


    if indoor_temp_str and indoor_humidity_str:
        draw.text((470, 303), indoor_temp_str, font=font18, fill=black)
        draw.text((470, 345), indoor_humidity_str, font=font18, fill=black)

    

    
    # Save the image for display as PNG
    screen_output_file = os.path.join(picdir, 'screen_output.png')
    template.save(screen_output_file)
    # Close the template file
    template.close()
    
    # Refresh clear screen to avoid burn-in at 3:00 AM
    if datetime.now().strftime('%H') == '03':
        print('Clearning screen to avoid burn-in.')
        epd.Clear()

# Set the fonts
font22 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 22)
font18 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 18)
font30 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 35)
font50 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 50)
font60 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 60)
font100 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 100)
font160 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 160)
# Set the colors
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'
grey = 'rgb(235,235,235)'

# Initialize and clear screen
print('Initializing and clearing screen.')
epd.init()
epd.Clear()



API_KEY = '41c8b07d76c2aa72fea313756e37b58c'
LOCATION = 'London'
LATITUDE = '51.509865'
LONGITUDE = '-0.118092'
UNITS = 'metric'


BASE_URL = 'http://api.openweathermap.org/data/2.5/onecall?' 
URL = BASE_URL + 'lat=' + LATITUDE + '&lon=' + LONGITUDE + '&units=' + UNITS +'&appid=' + API_KEY
try:
    while True:
        print("in the loop...")
        generate_output_image()
                
        
            

        if update_weather:
            write_to_screen(screen_output_file, 0)
            update_weather = False
        else:
            write_to_screen(screen_output_file, 600)

except KeyboardInterrupt:
    print("Interrupted by user, exiting...")
finally:
    # Clean up GPIO resources
    GPIO.cleanup()
    print("GPIO cleanup completed.")