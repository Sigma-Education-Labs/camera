# Operation of the test camera
Test camera: B0068 Arducam 5MP module <br>

## Wiring
The wiring allows for control over both SPI and I2C
| Arducam     | Raspberry Pi |
| ----------- | -----------  |
| VCC         | +5V          |
| GND         | GND          |
| SCL         | GPIO 3       |
| SDA         | GPIO 2       |
| SCK         | GPIO 11      |
| MISO        | GPIO 9       |
| MOSI        | GPIO 10      |
| CS          | GPIO 8       |
![Arducam <--> RPI wiring](arducam_rpi_schem.jpg)

