import tkinter as tk
from tkinter import scrolledtext
import requests
import threading
import random
import json
import os
import ctypes
import ctypes.wintypes
import winsound

# ======================================
# HEROBRINE DESKTOP PET V2
# ======================================

MODEL = "llama3.2:3b"
API = "http://localhost:11434/api/chat"

BASE = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE, "herobrine_memory.json")

WIDTH = 150
HEIGHT = 190
BG = "#ff00ff"
SPEED = 2

memory = []
memory_lock = threading.Lock()

# ======================================
# MEMORY
# ======================================

def load_memory():
    global memory

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)[-30:]
    except (OSError, json.JSONDecodeError):
        memory = []

def save_memory():
    try:
        with memory_lock:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(memory[-30:], f, indent=2)
    except OSError as e:
        print("Memory error:", e)

load_memory()

# ======================================
# OLLAMA AI
# ======================================

def ask_herobrine(question):
    with memory_lock:
        memory.append({"role": "user", "content": question})

        try:
            response = requests.post(
                API,
                json={
                    "model": MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are Herobrine from Minecraft. "
                                "You are mysterious, creepy and funny. "
                                "You have glowing white eyes. "
                                "Remember previous conversations. "
                                "Keep responses short."
                            )
                        },
                        *memory[-20:]
                    ],
                    "stream": False
                },
                timeout=180
            )

            response.raise_for_status()
            answer = response.json()["message"]["content"]

            memory.append({
                "role": "assistant",
                "content": answer
            })

            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(memory[-30:], f, indent=2)

            return answer

        except Exception as e:
            memory.pop()
            return "I cannot reach your world... " + str(e)

# ======================================
# WINDOW
# ======================================

root = tk.Tk()
root.title("Herobrine V2")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg=BG)
root.wm_attributes("-transparentcolor", BG)

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg=BG,
    highlightthickness=0
)
canvas.pack()

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

x = screen_w // 2
y = screen_h - HEIGHT

edge = 0
frame = 0
bubble = ""
bubble_timer = 0

# ======================================
# SOUND
# ======================================

def sound(freq=350, duration=120):
    def play():
        try:
            winsound.Beep(freq, duration)
        except RuntimeError:
            pass

    threading.Thread(target=play, daemon=True).start()

# ======================================
# SPEECH
# ======================================

def say(message):
    global bubble, bubble_timer

    bubble = message[:75]
    bubble_timer = 65

    sound(350, 100)

# ======================================
# DRAW HEROBRINE
# ======================================

def rect(x1, y1, x2, y2, color):
    canvas.create_rectangle(
        x1, y1, x2, y2,
        fill=color,
        outline=color
    )

def draw_pet():
    canvas.delete("all")

    if bubble_timer > 0:
        canvas.create_rectangle(
            2, 2, 148, 44,
            fill="white",
            outline="black",
            width=2
        )

        canvas.create_text(
            75, 23,
            text=bubble,
            fill="black",
            font=("Arial", 8, "bold"),
            width=138
        )

    try:
        point = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        mx = point.x
        look = max(-4, min(4, (mx - (x + 75)) // 35))
    except Exception:
        look = 0

    leg = 4 if frame % 2 else -4

    # Hair
    rect(36, 51, 114, 86, "#302017")

    # Face
    rect(42, 69, 108, 119, "#c69b73")

    # White eyes
    rect(51 + look, 86, 67 + look, 94, "white")
    rect(82 + look, 86, 98 + look, 94, "white")

    # Body
    rect(39, 119, 111, 157, "#2865a3")

    # Arms
    rect(22, 120, 39, 160, "#2865a3")
    rect(111, 120, 128, 160, "#2865a3")

    # Hands
    rect(22, 160, 39, 170, "#c69b73")
    rect(111, 160, 128, 170, "#c69b73")

    # Legs
    rect(44, 157, 70, 178 + leg, "#292929")
    rect(80, 157, 106, 178 - leg, "#292929")

    # Shoes
    rect(40, 178 + leg, 72, 185 + leg, "#111111")
    rect(78, 178 - leg, 110, 185 - leg, "#111111")

# ======================================
# WALL MOVEMENT
# ======================================

def move_pet():
    global x, y, edge

    if edge == 0:
        x += SPEED
        y = screen_h - HEIGHT

        if x >= screen_w - WIDTH:
            x = screen_w - WIDTH
            edge = 1

    elif edge == 1:
        y -= SPEED

        if y <= 0:
            y = 0
            edge = 2

    elif edge == 2:
        x -= SPEED
        y = 0

        if x <= 0:
            x = 0
            edge = 3

    elif edge == 3:
        y += SPEED

        if y >= screen_h - HEIGHT:
            y = screen_h - HEIGHT
            edge = 0

# ======================================
# TELEPORT
# ======================================

def teleport():
    global x, y, edge

    root.withdraw()

    def appear():
        global x, y, edge

        edge = random.randint(0, 3)

        if edge == 0:
            x = random.randint(0, screen_w - WIDTH)
            y = screen_h - HEIGHT
        elif edge == 1:
            x = screen_w - WIDTH
            y = random.randint(0, screen_h - HEIGHT)
        elif edge == 2:
            x = random.randint(0, screen_w - WIDTH)
            y = 0
        else:
            x = 0
            y = random.randint(0, screen_h - HEIGHT)

        root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")
        root.deiconify()
        say("Miss me?")

    root.after(1000, appear)

# ======================================
# RANDOM JUMPSCARE
# ======================================

def jumpscare():
    popup = tk.Toplevel(root)
    popup.title("Herobrine")
    popup.configure(bg="#000000")
    popup.attributes("-topmost", True)
    popup.attributes("-fullscreen", True)

    scare_color = random.choice(["#000000", "#120000", "#050505"])
    popup.configure(bg=scare_color)

    tk.Label(
        popup,
        text="👁️",
        font=("Segoe UI Emoji", 180, "bold"),
        bg=scare_color,
        fg="white"
    ).pack(expand=True)

    tk.Label(
        popup,
        text=random.choice([
            "I SEE YOU!",
            "HELLO STEVE!",
            "LOOK BEHIND YOU!",
            "FOUND YOU!",
            "BOO!",
            "NICE DESKTOP...",
            "YOU CANNOT HIDE!"
        ]),
        font=("Consolas", 38, "bold"),
        fg="white",
        bg=scare_color
    ).pack(pady=25)

    tk.Label(
        popup,
        text="HEROBRINE IS WATCHING.",
        font=("Consolas", 18, "bold"),
        fg="#aaaaaa",
        bg=scare_color
    ).pack(pady=20)

    def close_scare(event=None):
        if popup.winfo_exists():
            popup.destroy()

    popup.bind("<Escape>", close_scare)
    popup.after(random.randint(1800, 2800), close_scare)

    sound(random.randint(400, 650), random.randint(120, 220))


# ======================================
# CHAT
# ======================================

def open_chat():
    chat = tk.Toplevel(root)
    chat.title("Herobrine AI")
    chat.geometry("430x480")
    chat.attributes("-topmost", True)

    tk.Label(
        chat,
        text="HEROBRINE AI",
        font=("Consolas", 20, "bold")
    ).pack(pady=10)

    output = scrolledtext.ScrolledText(
        chat,
        wrap=tk.WORD,
        font=("Consolas", 10)
    )
    output.pack(fill="both", expand=True, padx=10)

    output.insert("end", "Herobrine: You're back...\n\n")

    with memory_lock:
        recent = memory[-10:].copy()

    for item in recent:
        name = "You" if item["role"] == "user" else "Herobrine"
        output.insert("end", name + ": " + item["content"] + "\n\n")

    output.configure(state="disabled")

    entry = tk.Entry(chat, font=("Consolas", 12))
    entry.pack(fill="x", padx=10, pady=10)

    def send():
        question = entry.get().strip()
        if not question:
            return

        entry.delete(0, "end")

        output.configure(state="normal")
        output.insert("end", "You: " + question + "\n")
        output.insert("end", "Herobrine is thinking...\n\n")
        output.configure(state="disabled")

        def worker():
            answer = ask_herobrine(question)

            def display():
                if not chat.winfo_exists():
                    return

                output.configure(state="normal")
                output.insert("end", "Herobrine: " + answer + "\n\n")
                output.configure(state="disabled")
                output.see("end")
                say(answer[:70])

            root.after(0, display)

        threading.Thread(target=worker, daemon=True).start()

    tk.Button(chat, text="Send", command=send).pack(pady=5)
    entry.bind("<Return>", lambda event: send())

# ======================================
# RANDOM EVENT TIMER
# ======================================

def random_event():
    event = random.choices(
        ["talk", "teleport", "jumpscare"],
        weights=[55, 25, 20]
    )[0]

    if event == "talk":
        say(random.choice([
            "I am watching...",
            "Hello Steve.",
            "Nice computer.",
            "Where are you going?",
            "I remember you.",
            "..."
        ]))

    elif event == "teleport":
        teleport()

    elif event == "jumpscare":
        jumpscare()

    # New random interval: 2–5 minutes
    root.after(random.randint(120000, 300000), random_event)

# ======================================
# ANIMATION
# ======================================

def animate():
    global frame, bubble_timer, bubble

    frame += 1
    move_pet()

    if bubble_timer > 0:
        bubble_timer -= 1
    else:
        bubble = ""

    draw_pet()

    root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

    root.after(80, animate)

# ======================================
# MENU
# ======================================

menu = tk.Menu(root, tearoff=0)

menu.add_command(label="Talk to Herobrine", command=open_chat)
menu.add_command(label="Teleport", command=teleport)
menu.add_command(label="JUMPSCARE!", command=jumpscare)
menu.add_separator()
menu.add_command(label="Exit", command=root.destroy)

canvas.bind("<Button-1>", lambda event: open_chat())
canvas.bind(
    "<Button-3>",
    lambda event: menu.tk_popup(event.x_root, event.y_root)
)

# ======================================
# START
# ======================================

print("Herobrine V2 started!")
print("Random jumpscares enabled.")
print("Ollama model:", MODEL)

say("I am back...")

draw_pet()
animate()

# First random event after 30–90 seconds
root.after(random.randint(30000, 90000), random_event)

root.mainloop()
