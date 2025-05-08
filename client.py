import threading
import socket
import subprocess
import wave
import threading
import os
import pyaudio
import audioop
from queue import Queue
from faster_whisper import WhisperModel

from movements import step_forward

#GLOBALS
IP_ADDR = "172.20.10.5" #last number is 8 if on jwang (maybe), 5 for kevin
PORT = 10000

#PIPER SETTINGS
PIPER_EXECUTABLE = "/home/jwang/piper/piper"
VOICE_DIR = "/home/jwang"
ONNX_PATH = os.path.join(VOICE_DIR, "en_US-arctic-medium.onnx")
CONFIG_PATH = os.path.join(VOICE_DIR, "en_US-arctic-medium.onnx.json")
PIPER_OUTPUT_WAV = "output.wav"

#RECORDING SETTINGS
OUTPUT_FILE = "recording.wav"
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 2048
FORMAT = pyaudio.paInt16

# === Audio Recording ===
def record_audio(mic_index):
    frames = []
    rms_queue = []
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=SAMPLE_RATE,
                     input=True,
                     input_device_index=mic_index,
                     frames_per_buffer=CHUNK)

    while sum(rms_queue) < 12000:
        if len(rms_queue) > 10:
            rms_queue = rms_queue[1:]
        data = stream.read(CHUNK, exception_on_overflow=False)
        rms_queue.append(audioop.rms(data, 2))
        pass

    print("🎤 Recording... Press Enter to stop.")

    while sum(rms_queue) > 11000:
        if len(rms_queue) > 10:
            rms_queue = rms_queue[1:]
        data = stream.read(CHUNK, exception_on_overflow=False)
        rms_queue.append(audioop.rms(data, 2))
        frames.append(data)

    print("🛑 Stopping recording...")
    stream.stop_stream()
    stream.close()
    pa.terminate()

    # Save to WAV file
    wf = wave.open(OUTPUT_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"✅ Audio saved to {OUTPUT_FILE}")

# === Transcribe using Whisper ===
def transcribe_audio(model):
    print("🧠 Transcribing...")
    segments, info = model.transcribe(OUTPUT_FILE)

    print("🌐 Detected language:", info.language)
    transcript = ""
    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
        transcript += segment.text + " "

    os.remove(OUTPUT_FILE)
    return transcript.strip()

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
	model = WhisperModel("tiny")  # Use "tiny" for spee
	
	while True:
		print("start speaking")
		
		record_audio(MIC_INDEX)
		input_text = transcribe_audio(model)
       		#input_text = input("Enter Prompt Here: (To be replaced with STT): ")
		text = retrieve_text_from_input(input_text)
		
		if "move forward" in input_text:
			move_thread = threading.Thread(target=step_forward, name="move_thread")
			move_thread.start()
		speak_text(text, SPEAKER_CARD)


