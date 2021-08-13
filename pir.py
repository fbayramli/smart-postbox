import RPi.GPIO as GPIO
from time import sleep
import requests

# Pin Setup:
PIR_PIN = 8
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIR_PIN, GPIO.IN)


def main():
    window = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    i = 0
    while True:
        try:
            pir_val = GPIO.input(PIR_PIN)
            window[i] = pir_val
            i = (i + 1) & 15
            if i == 0:
                print(window, sum(window))
                if sum(window) >= 12:
                    print("Sending signal to take picture...")
                    requests.get("http://192.168.0.150:5000/pir")
                    # Reset windows after successful detection
                    window = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    sleep(5)
        except Exception:
            print("No connection.")
        finally:
            sleep(0.01)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting gracefully.")
    finally:
        GPIO.cleanup()
