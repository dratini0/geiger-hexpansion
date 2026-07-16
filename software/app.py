import asyncio
import app
import time
from app_components import clear_background
from events.input import Buttons, BUTTON_TYPES
from machine import ADC, Pin, PWM
from system.hexpansion.config import HexpansionConfig
from system.eventbus import eventbus
from system.scheduler.events import RequestForegroundPushEvent
from collections import deque

class GeigerApp(app.App):
    def __init__(self, config=None):
        self.button_states = Buttons(self)
        super().__init__()
        self.hexpansion_config = config or HexpansionConfig(5)
        self.foregrounded = False
        self.voltage = 0.0
        self.pulses = deque([], 20)
        self.need_click = False
        
        pwm_pin, adc_pin, self.pulse, self.click = self.hexpansion_config.pin
        self.pwm = PWM(pwm_pin, freq=3000, duty_u16=32768) 
        self.adc = ADC(adc_pin, atten=ADC.ATTN_6DB)
        self.pulse.init(Pin.IN)
        self.click.init(Pin.OUT)
        self.pulse.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_pulse)

    def handle_pulse(self, _pin):
        self.pulses.append(time.ticks_us())
        self.need_click = True

    def update(self, delta):
        if not self.foregrounded: # Bring the app to the foreground on first run
            eventbus.emit(RequestForegroundPushEvent(self))
            self.foregrounded = True

        if self.need_click:
            self.click.on()
            time.sleep_us(100)
            self.click.off()
            self.need_click = False

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

    def draw(self, ctx):
        ctx.save()
        clear_background(ctx)
        ctx.text_align = ctx.CENTER
        ctx.rgb(1, 1, 1).move_to(0,-40).text(f"V_A = {round(self.voltage)} V")
        if len(self.pulses) >= 10:
            time_elapsed_us = time.ticks_diff(time.ticks_us(), self.pulses[0])
            count = len(self.pulses)
            cpm = count * 60_000_000 / time_elapsed_us
            ctx.move_to(0, 20).text(str(round(cpm)))
        else:
            ctx.move_to(0, 20).text("???")
        ctx.move_to(0, 50).text("CPM")
        ctx.restore()

    async def background_task(self):
        while True:
            await asyncio.sleep(0.1)
            self.voltage = self.adc.read_uv() / 1e6 * 310
            scale = (4 + 380.0 / self.voltage) / 5
            new_duty = min(max(round(self.pwm.duty_u16() * scale), 8192), 52428)
            self.pwm.duty_u16(new_duty)
            if not (360 <= self.voltage <= 400):
                self.pulses = deque([], 20)

    def deinit(self):
        self.pwm.deinit()
        self.adc.deinit()
        self.clock.deinit()
        self.pulse.deinit()

__app_export__ = GeigerApp
