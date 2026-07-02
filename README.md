# Geiger counter hexpansion

## High voltage generator

The high voltage power supply uses a microcontroller PWM peripheral, and a uses an ADC for feedback.
This means that it can only work on the ADC side of the Tildagon.
It also means that the power supply is completely dependent on software.

## Buzzer

Instead of connecting the speaker directly to the pulse detector, it is attached to the MCU.
This way, the clicking can be muted in software.
Alternatively, there is a solder jumper to short.

## Acknowledgements

Uses the [hexpansion template from EMF](https://github.com/emfcamp/badge-2024-hardware/tree/main/hexpansion)

Schematic loosely based on [Mightyohm's](https://mightyohm.com/blog/products/geiger-counter/) and [BroHogan's](https://sites.google.com/site/diygeigercounter/home) designs.
