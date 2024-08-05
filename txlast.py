from machine import Pin, I2C, UART
import time

# ESP32 - Pin assignment for I2C and UART
I2C_SCL_PIN_BME = 22  # SCL pin for BME280
I2C_SDA_PIN_BME = 21  # SDA pin for BME280

I2C_SCL_PIN_SI = 32  # SCL pin for SI7021
I2C_SDA_PIN_SI = 33  # SDA pin for SI7021

E32_UART_NUM = 2
E32_TX_PIN = 17
E32_RX_PIN = 16
BAUD_RATE = 9600

# Create I2C objects for BME280 and SI7021 sensors
i2c_bme = I2C(scl=Pin(I2C_SCL_PIN_BME), sda=Pin(I2C_SDA_PIN_BME), freq=10000)
i2c_si = I2C(0, scl=Pin(I2C_SCL_PIN_SI), sda=Pin(I2C_SDA_PIN_SI), freq=100000)

# Create UART object for E32 module
uart_e32 = UART(E32_UART_NUM, baudrate=BAUD_RATE, tx=Pin(E32_TX_PIN), rx=Pin(E32_RX_PIN))

# Function to read temperature and pressure from BME280
def read_bme280():
    try:
        import BME280  # Import BME280 module here to avoid module not found errors
        bme = BME280.BME280(i2c=i2c_bme)
        temp = bme.temperature
        pres = bme.pressure
        return temp, pres
    except Exception as e:
        print("Error reading BME280 sensor:", e)
        return None, None

# Function to read humidity from SI7021 sensor
def read_si7021():
    try:
        # Request humidity measurement
        i2c_si.writeto(0x40, b'\xF5')
        time.sleep(0.5)
        data = i2c_si.readfrom(0x40, 2)
        humidity = ((data[0] << 8) + data[1]) * 125 / 65536 - 6
        return humidity
    except OSError as e:
        print("Failed to read from SI7021 sensor:", e)
        return None

# Function to send data via E32 module

def send_data_to_e32(temp, pres, humidity):
    try:
        # Remove units from temperature and pressure
        temp_value = temp[:-1]  # Remove last character (unit)
        pres_value = pres[:-3]  # Remove last three characters (unit)
        
        # Format data
        data = f"{temp_value},{pres_value},{humidity}"

        # Send data via UART to E32 module
        uart_e32.write(data + '\r\n')
        
        # Print sent data
        print(f"Sent data - Temp: {temp_value}, Pres: {pres_value}, Humidity: {humidity}")
    except Exception as e:
        print("Failed to send data via E32:", e)

# Main loop to read sensors and send data
while True:
    try:
        # Read BME280 sensor data
        temp, pres = read_bme280()
        
        # Read SI7021 sensor data (humidity)
        humidity = read_si7021()
        
        # Send data via E32 module if all sensor readings are valid
        if temp is not None and pres is not None and humidity is not None:
            send_data_to_e32(temp, pres, humidity)
        else:
            print("Invalid sensor readings. Skipping sending data.")
        
    except Exception as e:
        print("Main loop error:", e)
    
    # Delay before looping again
    time.sleep(1)
