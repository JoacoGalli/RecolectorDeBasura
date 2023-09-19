import drivers
import RPi.GPIO as GPIO
import subprocess
import signal
from time import sleep, time

GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 20
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Cuando no uso el boton, esta en alto.

display = drivers.Lcd()
count = 0
program_running = False
program_process = None

def switch_state(channel):
    global count, program_running, program_process

    if program_running:
        # Send a signal to the subprocess to stop it gracefully
        program_process.send_signal(signal.SIGTERM)
        program_process.wait()
        program_running = False
    else:
        count = 1 - count
        if count == 1:
            try:
                program_process = subprocess.Popen(["python", "control.py"])
                program_running = True
            except Exception as e:
                print("Error:", e)

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=switch_state, bouncetime=300)

try:
	display.lcd_display_string("Welcome!", 1)
	sleep(2)
	display.lcd_clear()
	while True:
		if count == 0:
			display.lcd_display_string("Status: Off", 1)
			display.lcd_display_string("boton to start ", 2)
		else:
			display.lcd_display_string("Status: On ", 1)
			display.lcd_display_string("2 boton to stop", 2)

		sleep(0.1)

except KeyboardInterrupt:
    print("Cleaning up!")
    display.lcd_clear()
    GPIO.cleanup()
    if program_running:
        program_process.send_signal(signal.SIGTERM)
        program_process.wait()
