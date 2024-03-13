import network
import urequests
import ujson
import time
from config import WIFI_SSID, WIFI_PASSWORD, THINGSPEAK_API_KEY, THINGSPEAK_URL, LOOP_DELAY_TIME
from max31855 import MAX31855
from pulse_count import PulseCounter
from machine import SPI, Pin
import network

def setup_temp():
    spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
    print(f"We got the following SPI values: {spi}")
    cs = Pin(13, Pin.OUT)
    print(f"We got the following CS values: {cs}")
    tc = MAX31855(spi, cs)
    return tc

def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to WiFi...")
        sta_if.active(True)
        if WIFI_PASSWORD:
            sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        else:
            sta_if.connect(WIFI_SSID)
        while not sta_if.isconnected():
            time.sleep(1)
    print("Connected to WiFi:", sta_if.ifconfig())

def send_thingspeak_update(data: dict):
    # Extend data with the API key
    data["api_key"] = THINGSPEAK_API_KEY
    headers = {"Content-Type": "application/json"}
    try:
        resp = urequests.post(THINGSPEAK_URL, data=ujson.dumps(data), headers=headers)
        resp.close()
        print("ThingSpeak update sent")
    except Exception as e:
        print("Failed to send update to ThingSpeak:", e)

def main():
    #connect_wifi()
    oscillator_pin = Pin(14, Pin.OUT)
    pulse_measurement_pin = 15
    measurement_period = 10
    thermo_couple = setup_temp()
    print("Thermocouple setup complete")
    pulse_counter = PulseCounter(pulse_measurement_pin, measurement_period)
    print("Pulse counter setup complete")
    while True:
        # Measure the pulse width when the oscillator is in the low state
        print("Measuring low pulse width")
        time.sleep_ms(500)
        oscillator_pin.low()
        time.sleep_ms(500)
        pulse_time_low = pulse_counter.measure()
        print(f"Pulse time low: {pulse_time_low} ns")
        time.sleep_ms(500)
        print("Measuring high pulse width")
        oscillator_pin.high()
        time.sleep_ms(500)
        pulse_time_high = pulse_counter.measure()
        print(f"Pulse time high: {1/(pulse_time_high/1e12):0.3f} Hz")
        try:
            temp = thermo_couple.temp
            message = "OK"
        except RuntimeError as e:
            print("Failed to read thermocouple:", e)
            temp = "NaN"
            message = "Failed to read thermocouple: " + str(e)
        # Upload data
        data = {
            "field1": temp,
            "field2": pulse_time_low, # This gives the higher frequency and lower period because the relay is shorting out the resistor that
            "field3": pulse_time_high,
            "field4": message
        }
        #print(f"Sending update to ThingSpeak: {data}")
        print(data)
        time.sleep(1)
        send_thingspeak_update(data)
        time.sleep(LOOP_DELAY_TIME)

if __name__ == "__main__":
    main()
