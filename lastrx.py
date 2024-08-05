from machine import Pin, UART
import time

# ESP32 - Pin assignment for UART
E32_UART_NUM = 2
E32_TX_PIN = 17
E32_RX_PIN = 16
BAUD_RATE = 9600

# Create UART object for E32 module
uart_e32 = UART(E32_UART_NUM, baudrate=BAUD_RATE, tx=Pin(E32_TX_PIN), rx=Pin(E32_RX_PIN))

# Function to fetch data via E32 module
def fetch_data_from_e32():
    try:
        # Wait for data from E32 module via UART
        if uart_e32.any():
            received_data = uart_e32.read()
            return received_data
        else:
            return None
    except Exception as e:
        print("Failed to fetch data via E32:", e)
        return None

# Main loop to fetch and process data from ESP32 #1 via E32 module
while True:
    try:
        # Fetch data from ESP32 #1 via E32 module
        received_data = fetch_data_from_e32()
        
        if received_data:
            print(received_data.decode().strip())  # Print only the numeric data
        
        # Optionally, process fetched data further
        
    except Exception as e:
        print("Main loop error:", e)
    
    # Delay before looping again
    time.sleep(1)

