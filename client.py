import socket
import subprocess
import wave
import threading
import os
import pyaudio



#GLOBALS
IP_ADDR = "172.20.10.8"
PORT = 10000

#PIPER SETTINGS
PIPER_EXECUTABLE = "/home/jwang/piper/piper"
VOICE_DIR = "/home/jwang"
ONNX_PATH = os.path.join(VOICE_DIR, "en_US-arctic-medium.onnx")
CONFIG_PATH = os.path.join(VOICE_DIR, "en_US-arctic-medium.onnx.json")
PIPER_OUTPUT_WAV = "output.wav"

#RECORDING SETTINGS
OUTPUT_FILE = "recording.wav"
SAMPLE_RAT = 16000
CHANNELS = 1
CHUNK = 1024
FORMAT = pyaudio.paInt16

def find_mic_index(name_keyword="Samson"):
	pa = pyaudio.PyAudio()
	for i in range(pa.get_device_count()):
		info = pa.get_device_info_by_index(i)
		if name_keyword.lower() in info["name"].lower() and info["maxInputChannels"] > 0:
			return i
	return None

def find_speaker_card(name_keyword="UACDemoV10"):
	result = subprocess.run(["aplay", "-l"], capture_output=True, text=True)
	card_number = None
	for line in result.stdout.splitlines():
		if name_keyword in line and "card" in line:
			parts = line.split()
			try:
				idx = parts.index("card")
				card_number = parts[idx + 1].rstrip(":")
				return card_number
			except (ValueError, IndexError):
				continue
	return None

def retrieve_text_from_input(input):
	with socket.socket() as client:
		client.connect((IP_ADDR, PORT))
		client.settimeout(10)

		request = (input).encode("utf-8")
		client.sendall(request)
		client.shutdown(socket.SHUT_WR)
		
		text = client.recv(1024).decode("utf-8")
		return text

def speak_text(test, speaker_card):
	print("tts started")
	try: 
		tts_cmd = [
			PIPER_EXECUTABLE,
			"--model", ONNX_PATH, "--config", CONFIG_PATH, "--output_file", PIPER_OUTPUT_WAV, "--stdin" ]
		subprocess.run(tts_cmd, input=text.encode(), check=True)
		
		subprocess.run(["aplay", "-D", f"plughw:{speaker_card},0", PIPER_OUTPUT_WAV], check=True)
	except subprocess.CalledProcessError as e:
		print("Error", e)


if __name__ == "__main__":
	MIC_INDEX = find_mic_index()
	SPEAKER_CARD = find_speaker_card()
	
	if MIC_INDEX is None or SPEAKER_CARD is None:
		raise RuntimeError("one of the devices cannot be found")
	
	input_text = input("Enter Prompt Here: (To be replaced with STT): ")
	text = retrieve_text_from_input(input_text)
	speak_text(text, SPEAKER_CARD)
