SERIAL_PORT=/dev/cu.usbmodem*
SERIAL_PORT=/dev/ttyACM0
ampy --delay=5 --port $SERIAL_PORT put main.py && \
ampy --delay=5 --port $SERIAL_PORT put pulse_count.py && \
ampy --delay=5 --port $SERIAL_PORT put config.py && \
ampy --delay=5 --port $SERIAL_PORT put max31855_micro_python/src/max31855.py && \
ampy --delay=5 --port $SERIAL_PORT run main.py
