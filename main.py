from machine import Pin, Timer
import time



class PulseCounter:

    def __init__(self, input_pin_number: int, measurement_period_ms: int = 1000):
        self.measurement_period_ms = measurement_period_ms
        self.input_pin = Pin(input_pin_number, Pin.IN, Pin.PULL_UP)
        self.ticks = 0
        self.ticks_prev = 0
        self.pulse_width = 0

    def irq_handler(self, pin):
        self.ticks = time.time_ns()
        self.pulse_width = self.ticks - self.ticks_prev
        self.ticks_prev = self.ticks

    def measure(self):
        # Set up the interrupt
        self.input_pin.irq(trigger=Pin.IRQ_RISING, handler=self.irq_handler)
        time.sleep_ms(self.measurement_period_ms)
        self.input_pin.irq(handler=None)
        return self.pulse_width


if __name__ == "__main__":
    fm = PulseCounter(15, 10)
    while True:
        print(fm.measure())
        time.sleep_ms(15)
