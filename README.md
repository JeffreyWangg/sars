## SARS

SARS is a "semi-autonomous robotic system" that responds to voice commands and communicates to the user.

## How to Run

You need an external Raspberry Pi. Connect a USB microphone and speaker to the Raspberry Pi and connect both the Raspberry Pi and your server device to the same network. The server device should run 
server.py and the Raspberry Pi should run client.py. client.py will start a loop where you can talk to the microphone, and it should send a request to the server device which should generate
text and respond.
