import socket
import re
from mlx_lm import load, generate

emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        "]+", flags=re.UNICODE)
prepend = "You are a witty and crude robotic assistant named SARS who speaks in short sentences."

model, tokenizer = load("mlx-community/Mistral-7B-Instruct-v0.3-4bit")

base_template = [
    {"role": "user", "content": prepend}, 
    {"role": "assistant", "content": "Understood."},
    {'role': 'user', 'content': 'How are you?'}, 
    {'role': 'assistant', 'content': "I'm doing great! But I'm here to help you, so let's get this party started, shall we?"}, 
    ]

history = []

server = socket.socket()
server.bind(("", 10000))

server.listen()
print ('server started and listening')
while True:
    if len(history) > 9:
        history = history[2:]
    conn, addr = server.accept()
    print("connection found!")
    data = conn.recv(1024).decode()
    print(data)
    prompt = data
    history += [{"role": "user", "content": prompt}]

    print(base_template + history)
    prompt = tokenizer.apply_chat_template(
        base_template + history, add_generation_prompt=True
    )
    text = generate(model, tokenizer, prompt=prompt, max_tokens=120)
    text = emoji_pattern.sub(r'', text)
    print(text)
    history += [{"role": "assistant", "content": text}]
    response = text
    conn.send(response.encode("utf-8"))
    
