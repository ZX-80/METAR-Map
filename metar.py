"""A script to manage METAR map LED strips."""

import configparser
import math
import random
import urllib.request
import xml.etree.ElementTree as XMLTree
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Self

import adafruit_ads1x15.ads1115 as ADS
import board
import busio
import digitalio
import neopixel
from adafruit_ads1x15.analog_in import AnalogIn

LED_COUNT = 100
MAX_ANALOG_VALUE = 32752.0
WEATHER_API_URL = "https://aviationweather.gov/api/data/metar?format=xml&taf=false"
CONFIG = configparser.ConfigParser()
CONFIG_FILE = "metar.ini"  # Used for saving states between executions
STATION_FILE = Path.home() / Path("stations.dat")  # LED to station mappings (line# = LED)


# LED data
class METARColors(Enum):
    """The LED color for each flight category."""

    VFR = (255, 0, 0)  # Red, Visual Flight Rules
    MVFR = (0, 0, 255)  # Green, Marginal Visual Flight Rules
    IFR = (0, 255, 0)  # Blue, Instrument Flight Rules
    LIFR = (0, 125, 125)  # Magenta, Low Instrument Flight Rules
    UNKNOWN = (0, 0, 0)  # Off, No data


class LEDMode(Enum):
    """The current display mode."""

    LIVE = 0
    RAINBOW = 1
    DEMO = 2

    def succ(self) -> Self:
        """Return the successor mode, wrapping if needed."""
        return type(self)(self.value + 1 if self.value in type(self) else 0)


# Manage state
def load_ini() -> tuple[LEDMode, int]:
    """Load the state from disk."""
    CONFIG.read(CONFIG_FILE)
    mode = LEDMode(CONFIG.getint("STATE", "mode", fallback=LEDMode.LIVE.value))
    rainbow_phase = CONFIG.getint("STATE", "rainbow_phase", fallback=0)
    return mode, rainbow_phase


def save_ini(mode: LEDMode, rainbow_phase: int) -> None:
    """Save current state to disk."""
    CONFIG.set("STATE", "mode", str(mode.value))
    CONFIG.set("STATE", "rainbow_phase", str(rainbow_phase))
    with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
        CONFIG.write(config_file)


# Manage weather data
def fetch_weather() -> list[tuple[int, METARColors]]:
    """Fetch the latest weather from a government API."""

    # Read from API
    print("Connecting to weather API...")
    stations = STATION_FILE.read_text(encoding="utf-8").splitlines()[:LED_COUNT]
    url = f"{WEATHER_API_URL}&ids={"%2C".join(station_code for station_code in stations if station_code != "NULL")}"
    with urllib.request.urlopen(url) as weather_response:
        xml_root = XMLTree.fromstring(weather_response.read())

    # Collect weather information
    led_categories: list[tuple[int, METARColors]] = []  # Pixel ID, METAR flight category
    for metar in xml_root.iter("METAR"):
        if (station_id := metar.find("station_id")) and station_id.text:
            print(f"{station_id.text}:", end="")
            if (flight_category := metar.find("flight_category")) and flight_category.text:
                try:
                    category = METARColors[flight_category.text]
                except ValueError:
                    category = METARColors.UNKNOWN
                led_categories.append(
                    (stations.index(flight_category.text), category)
                )  # Use the linenumber as the LED index
                print(led_categories[-1][1].name)
            else:
                print("----")
    return led_categories


def main() -> None:
    """Manage LED colors."""

    # Initialize board
    button = digitalio.DigitalInOut(board.D4)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    brightness_pin = AnalogIn(ADS.ADS1115(busio.I2C(board.SCL, board.SDA)), ADS.P0)
    pixels = neopixel.NeoPixel(
        board.D18,
        LED_COUNT,
        brightness=brightness_pin.value / MAX_ANALOG_VALUE,
        pixel_order=neopixel.GRB,
        auto_write=False,
    )

    # Precomputed sine table for cycling LEDs using the sine fade technique
    sine_table = [math.floor((math.sin(math.radians(i)) + 1) * 127.5) for i in range(360)]
    previous_button_value = True  # Act as a falling edge trigger
    previous_mode: LEDMode | None = None
    mode, rainbow_phase = load_ini()
    while True:

        # Check inputs
        pixels.brightness = brightness_pin.value / MAX_ANALOG_VALUE
        if previous_button_value & ~(previous_button_value := button.value):
            mode = mode.succ()
            save_ini(mode, rainbow_phase)

        # Perform mode action
        match mode:
            case LEDMode.LIVE if mode != previous_mode:
                for pixel_index, station_id in fetch_weather():
                    pixels[pixel_index] = station_id

            case LEDMode.RAINBOW:
                rainbow_phase = (rainbow_phase + 1) % 360 if mode == previous_mode else 0
                pixels.fill(
                    (
                        sine_table[rainbow_phase],
                        sine_table[(rainbow_phase + 120) % 360],  # Phase shift by 120 degrees
                        sine_table[(rainbow_phase + 240) % 360],  # Phase shift by 240 degrees
                    )
                )

            case LEDMode.DEMO if mode != previous_mode:
                random.seed(1)  # For consistent results
                demo_metars = random.choices(list(METARColors)[:-1], k=100)
                for pixel_index, metar in enumerate(demo_metars):
                    pixels[pixel_index] = metar.value

        pixels.show()  # Display LEDs now that they're computed
        previous_mode = mode
        sleep(0.01)


if __name__ == "__main__":
    main()
