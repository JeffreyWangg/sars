import lgpio
import time

SERVO_L = 2
SERVO_R = 3 #bad one

FREQ=50

h = lgpio.gpiochip_open(4)

def move_arms_up():
	lgpio.tx_pwm(h, SERVO_R, FREQ, 4.5)
	lgpio.tx_pwm(h, SERVO_L, FREQ, 9)

def move_arms_down():
	lgpio.tx_pwm(h, SERVO_R, FREQ, 6)
	lgpio.tx_pwm(h, SERVO_L, FREQ, 7.5)

def rotate_left():
	lgpio.tx_pwm(h, SERVO_R, FREQ, 3)
	lgpio.tx_pwm(h, SERVO_L, FREQ, 8.5)
	time.sleep(1)
	lgpio.tx_pwm(h, SERVO_L, FREQ, 7.5) 

def step_forward():
	move_arms_up()
	time.sleep(1)
	move_arms_down()
	time.sleep(1)

if __name__ == "__main__":
	move_arms_down()
	time.sleep(2)
	try:
		while True:
			time.sleep(1)
			step_forward()
			time.sleep(1)
			step_forward()

	except KeyboardInterrupt:
		lgpio.tx_pwm(h, SERVO_L, FREQ, 50)
		lgpio.gpiochip_close(h)
