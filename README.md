# Raspberry-Pi-weather-Display-with-7.5-inch-B-W-E-papaer-Display
This project is a weather station that uses a Raspberry Pi, an e-paper display, a DHT22 temperature and humidity sensor, and an LED. It fetches weather data from the OpenWeatherMap API and displays it on the e-paper display, while also showing the indoor temperature and humidity from the DHT22 sensor. The LED turns on when the indoor temperature goes above a specified threshold.

Here's a summary of the main components and their functionalities:

Raspberry Pi: Acts as the central processing unit, running the Python script that fetches data from the OpenWeatherMap API, reads the DHT22 sensor, controls the LED, and updates the e-paper display.

e-paper display (Waveshare 7.5 inch V2): Displays the weather data, including current temperature, humidity, wind speed, weather conditions, and high/low temperatures. It also displays the indoor temperature and humidity read from the DHT22 sensor.

DHT22 temperature and humidity sensor: Measures the indoor temperature and humidity and provides data to the Raspberry Pi.

LED: Lights up when the indoor temperature goes above a specified threshold, which can be set in the code.

OpenWeatherMap API: Provides weather data for the specified location. The Python script fetches this data and processes it to display on the e-paper screen.

The code reads weather data from the OpenWeatherMap API, processes it, and generates an image with the information. The image is saved as 'screen_output.png' in the 'picture' directory. The script then sends this image to the e-paper display to show the weather information. Additionally, the script reads data from the DHT22 sensor to display indoor temperature and humidity and control the LED based on the indoor temperature.
# Here's the output image to be written to the screen
![image](https://user-images.githubusercontent.com/66757712/234220438-fde9c15a-325a-4424-bff5-19cff223b5b7.png)

# Here's the circuit diagram of the project
![image](https://user-images.githubusercontent.com/66757712/234220327-3b2832b5-97f2-4173-9e00-442644e41f19.png)
