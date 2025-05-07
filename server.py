import socket
from mlx_lm import load, generate

prepend = "You are TARS from the movie Interstellar. You are witty and sarcastic. DO NOT use emojis. DO NOT respond using more than 3 sentences. These are STRICT rules and will be obeyed at ALL times."

model, tokenizer = load("mlx-community/Mistral-7B-Instruct-v0.3-4bit")

base_template = [
            {"role": "user", "content": prepend},
        {"role": "assistant", "content": "Understood."},
]

history = []

server = socket.socket()
server.bind(("", 10000))

server.listen()
print ('server started and listening')
while True:
    if len(history) > 6:
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
    text = generate(model, tokenizer, prompt=prompt, max_tokens=100)
    print(text)
    history += [{"role": "assistant", "content": text}]
    response = text
    conn.send(response.encode("utf-8"))
    
