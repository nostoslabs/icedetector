import time
from machine import Pin, Timer
import _thread

def process_ticks():
    cpu_freq = time.cpu_freq()
    while True:
        if len(pulse_counter.ticks_queue) >= 2:
            prev_ticks = pulse_counter.ticks_queue.pop(0)
            curr_ticks = pulse_counter.ticks_queue.pop(0)
            pulse_width_cycles = curr_ticks - prev_ticks
            pulse_width_ns = pulse_width_cycles * (1_000_000_000 / cpu_freq)
            # Process the pulse width as needed
            print(f"Pulse width: {pulse_width_ns} ns")

class PulseCounter:
    def __init__(self, input_pin_number: int, measurement_period_ms: int = 1000):
        self.measurement_period_ms = measurement_period_ms
        self.input_pin = Pin(input_pin_number, Pin.IN, Pin.PULL_UP)
        self.ticks_queue = []  # Queue to store CPU ticks
        self.timer = Timer()

    def irq_handler(self, pin):
        self.ticks_queue.append(time.ticks_cpu())  # Store CPU ticks

    def measure(self):
        # Set up the interrupt
        self.input_pin.irq(trigger=Pin.IRQ_RISING, handler=self.irq_handler)

        # Create a timer to measure the period
        self.timer.init(period=self.measurement_period_ms, mode=Timer.ONE_SHOT, callback=lambda t: self.input_pin.irq(handler=None))

        # Wait for the timer to expire
        while not self.timer.callback():
            pass

        # Calculate the pulse width outside of the interrupt context
        if len(self.ticks_queue) >= 2:
            prev_ticks = self.ticks_queue.pop(0)
            curr_ticks = self.ticks_queue.pop(0)
            pulse_width_cycles = curr_ticks - prev_ticks
            return pulse_width_cycles
        else:
            return 0  # No pulse detected or invalid data

    # Optional: Create a separate thread or task to process the CPU ticks
    # _thread.start_new_thread(process_ticks, ())


pulse_counter = PulseCounter(15)

while True:
    pulse_width_cycles = pulse_counter.measure()
    if pulse_width_cycles:
        cpu_freq = time.cpu_freq()
        pulse_width_ns = pulse_width_cycles * (1000000000 / cpu_freq)
        print(f"Pulse width: {pulse_width_ns} ns")
    time.sleep_ms(150)
