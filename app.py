from flask import Flask, render_template, request, jsonify
import json
import os
import re

app = Flask(__name__)

# =========================================================
# 🧠 MEMORY SYSTEM
# =========================================================

MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)

    return {
        "knowledge": {},
        "unknown_questions": [],
        "chat_history": [],
        "name": None
    }


def save_memory(data):
    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=2)


memory = load_memory()

# =========================================================
# 🧹 CLEAN TEXT
# =========================================================

def clean(text):
    return re.sub(r"[^\w\s]", "", text.lower().strip())


# =========================================================
# 🧠 KNOWLEDGE ENGINE (STATIC BRAIN)
# =========================================================

def knowledge(msg):
    text = clean(msg)

    data = {
        # SPACE
        "sun": "The Sun is a star at the center of our solar system.",
        "moon": "The Moon is Earth's natural satellite.",
        "earth": "Earth is the third planet from the Sun.",
        "mars": "Mars is the Red Planet.",
        "jupiter": "Jupiter is the largest planet.",
        "saturn": "Saturn has rings.",
        "planets": "Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune",

        # PHYSICS
        "gravity": "Gravity is the force that pulls objects toward Earth.",
        "light": "Light is a form of energy that enables vision.",
        "sound": "Sound is vibration that travels through air.",
        "energy": "Energy is the ability to do work.",

        # CHEMISTRY
        "atom": "An atom is the smallest unit of matter.",
        "water": "Water is H2O.",
        "oxygen": "Oxygen is needed for breathing.",

        # GRAMMAR
        "noun": "A noun is a naming word.",
        "verb": "A verb is an action word.",

        # COUNTRIES
        "capital of ghana": "Accra",
        "capital of nigeria": "Abuja",
        "capital of liberia": "Monrovia"
    }

    for key in data:
        if key in text:
            return data[key]

    return None


# =========================================================
# 🧠 REASONING ENGINE
# =========================================================

def reasoning_fix(msg):
    text = clean(msg)

    if text.startswith("who is"):
        entity = text.replace("who is", "").strip()

        if entity == "newton":
            return "Isaac Newton discovered gravity and laws of motion."

        if entity == "einstein":
            return "Albert Einstein developed the theory of relativity."

        return f"I don't know who {entity} is yet. Teach me: {entity} is ..."

    if text.startswith("what is"):
        entity = text.replace("what is", "").strip()

        if entity == "light":
            return "Light is energy that allows vision."

        if entity == "sound":
            return "Sound is vibration traveling through air."

        return f"I don't know what {entity} is yet. Teach me: {entity} is ..."

    return None


# =========================================================
# 🧠 SELF LEARNING ENGINE
# =========================================================

def learn_system(user_message, memory):
    text = clean(user_message)

    # recall learned knowledge
    for key in memory["knowledge"]:
        if key in text:
            return memory["knowledge"][key]

    # teach mode
    if " is " in text:
        parts = text.split(" is ", 1)

        question = parts[0].strip()
        answer = parts[1].strip()

        memory["knowledge"][question] = answer
        save_memory(memory)

        return "Okay 👍 I will remember that."

    # unknown tracking
    if any(x in text for x in ["what", "who", "define", "explain"]):
        memory["unknown_questions"].append(text)
        save_memory(memory)

        return "I don't know that yet. You didn't teach me that."

    return None


# =========================================================
# 🧠 BRAIN SYSTEM
# =========================================================

def brain(msg, memory):
    text = clean(msg)

    if any(x in text for x in ["hello", "hi", "hey"]):
        return "Hello 👋 I am ScienX AI."

    if "how are you" in text:
        return "I am fully operational and learning."

    if "who are you" in text:
        return "I am ScienX AI — a learning assistant system."

    if memory.get("name") and "my name" in text:
        return f"You told me your name is {memory['name']}."

    return None


# =========================================================
# 🌐 ROUTES
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    global memory

    user_message = request.json.get("message", "")
    text = clean(user_message)

    # =========================
    # CHAT HISTORY
    # =========================
    memory["chat_history"].append(user_message)
    memory["chat_history"] = memory["chat_history"][-20:]
    save_memory(memory)

    # =========================
    # 1. MEMORY ACTIONS FIRST
    # =========================
    if "my name is" in text:
        name = user_message.replace("my name is", "").strip()
        memory["name"] = name
        save_memory(memory)
        return jsonify({"response": f"Nice to meet you {name}."})

    if "remember that" in text:
        fact = user_message.replace("remember that", "").strip()
        memory.setdefault("facts", []).append(fact)
        save_memory(memory)
        return jsonify({"response": f"I will remember: {fact}"})

    # =========================
    # 2. KNOWLEDGE ENGINE (FIXED PRIORITY)
    # =========================
    kb = knowledge(user_message)
    if kb:
        return jsonify({"response": kb})

    # =========================
    # 3. REASONING ENGINE
    # =========================
    reason = reasoning_fix(user_message)
    if reason:
        return jsonify({"response": reason})

    # =========================
    # 4. SELF LEARNING
    # =========================
    learned = learn_system(user_message, memory)
    if learned:
        return jsonify({"response": learned})

    # =========================
    # 5. BRAIN
    # =========================
    smart = brain(user_message, memory)
    if smart:
        return jsonify({"response": smart})

    # =========================
    # 6. DEFAULT
    # =========================
    return jsonify({
        "response": "ScienX AI did not understand. You can teach me: X is Y"
    })


# =========================================================
# 🚀 RUN (RENDER SAFE)
# =========================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
