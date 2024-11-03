<div align="center">

# 🌤️ Florida METAR Map ✈️

An aviation sectional map, using LEDs to display live Florida weather. 

Inspired by the amazing work by Sarah at [Making a LED powered METAR map for your wall](https://slingtsi.rueker.com/making-a-led-powered-metar-map-for-your-wall).

<p align = "center">
  <img width="550" src="https://github.com/user-attachments/assets/9d5b22dd-ee2a-4f99-a6d8-ca5aa2d37ca5">
</p>

*METAR(METeorological Aerodrome Report)s over Florida*
  
[What Is It?](#what-is-it) •
[How Does It Work?](#how-does-it-work) •
[BOM (Bill of Materials)](#bom-bill-of-materials)

</div>

# What Is It?

A METAR weather report is an hourly (typical) report of the local weather at a
specific airport. A report will have one of four categories, in order of good to bad: 

- VFR(visual flight rules) in green
- MVFR(Marginal VFR) in blue
- IFR(Instrument flight rules) in red
- LIFR(Low IFR) in magenta

I used LEDs behind a map of Florida to display
this live status for each airport on the map. As we can see from the above
image, the south is the only place with good weather, but it’s not great overall, with
lots of MVFR(red) and IFR(blue) weather.

# How Does It Work?

A raspberry
pi zero requests the Florida METARs from a government public api at
“https://www.aviationweather.gov”. It then reads the returned xml and sets the
LEDs accordingly. A pot is polled to decide the brightness of the LEDs. A cron
job was created that kills the current program(if it failed to die), and runs a
new one. This allows the pi to check the live weather every 5 minutes without
having the program run 24/7.

It has three
modes. The first is the normal mode as described above. The second cycles through colours as a de facto LED test mode. The last
shows a predefined map for demos, in the event we have good weather(all green LEDs).

# BOM (Bill of Materials)

<p align = "center">
  <img width="80%" src="https://github.com/user-attachments/assets/ad8bc85b-e36e-4213-b336-2cfc18b7b26d">
</p>

<div align="center">

  *Different stages of construction*

</div>

- **Poster:** I
created the VFR map of Florida from a much larger source (2017 Florida sectional 9506x8614) provided by the government, as there does not
exist one for all of Florida at the size needed. VFR charts show the airports along
with other related information, which was perfect for this project. 

- **Frame:** A 30x40 inch shadow box ([Amazon](https://www.amazon.com/gp/product/B0764QTCYP/)), perfect for the multi-layered foam and LEDs. 
The poster had to be remade unfortunately as the frame was smaller than
advertised.

- **RGB LEDs and foam boards(WS2811 12mm):**
These can be addressed using the neopixel library. I had to order two(fifty LEDs each) as I need sixty-one LEDs, and some are spaced
far apart. Five strips can be chained without needing extra power, so a chain of two was
fine. <br><br>
They were glued into holes drilled into three layers of foam boards cut to
size. Getting clean cut holes though foam is surprisingly difficult as it tends to be
messy, even with a drill. I used a box cutter to clean each one after it was
made. <br><br>
After cutting the boards, they were glued together, and then the poster
was glued on top. This was pressed into the frame. I used a type of spray glue
that allowed adjusting the poster position as it dried, since everything had to
be to the millimeter. 

- **Logarithmic slide potentiometer and button:** The button changes the mode, and the potentiometer changes the
brightness. 
The library used for button input caused freezes when used with the ADC
library, and hence had to be swapped out for a more low level one. It took a
while to figure out what caused the freezes, as there’s no screen on the Pi(it
uses ssh sessions).

- **ADS1115:**
Used to convert the analog signal from the pot to a digital signal that the Pi
can read. I didn’t realize until last minute that the raspberry pi has no Analog
pins, only digital ones. This was a huge issue, as the potentiometer, which is
polled for brightness, outputs a voltage from 0-5v, not a digital signal.

- **Raspberry Pi Zero W:** This is where I hosted the code to pull weather and update the pixels. It
is smaller than the normal Pi, and has built in wifi.
