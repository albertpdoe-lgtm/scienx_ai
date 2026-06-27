from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# =========================
# MEMORY SYSTEM
# =========================

MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)

    return {
        "knowledge": {},
        "unknown_questions": [],
        "chat_history": []
    }


def save_memory(data):
    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=2)


memory = load_memory()

# =========================
# 🧠 SELF LEARNING ENGINE
# =========================

def learn_system(user_message, memory):
    text = user_message.lower().strip()

    # 1. recall learned knowledge
    if text in memory["knowledge"]:
        return memory["knowledge"][text]

    # 2. teaching mode
    if " is " in user_message:
        parts = user_message.split(" is ", 1)
        if len(parts) == 2:
            question = parts[0].strip().lower()
            answer = parts[1].strip()

            memory["knowledge"][question] = answer
            save_memory(memory)

            return "Okay 👍 I will remember that."

    # 3. unknown question detection
    if any(x in text for x in ["what is", "who is", "define", "explain"]):
        memory["unknown_questions"].append(text)
        save_memory(memory)

        return "I don't know that yet. You didn't teach me that."

    return None


# =========================
# 🧠 BRAIN SYSTEM
# =========================

def brain(msg, memory):
    text = msg.lower().strip()

    if any(x in text for x in ["hello", "hi", "hey"]):
        return "Hello 👋 I am ScienX AI."

    if "how are you" in text:
        return "I am fully operational."

    if "who are you" in text:
        return "I am ScienX AI — a learning assistant system."

    if memory.get("name") and "my name" in text:
        return f"You told me your name is {memory['name']}."

    return None


# =========================
# 🌍 KNOWLEDGE ENGINE
# =========================

def knowledge(msg):
    text = msg.lower()

    # PLANETS
    if "planets" in text:
        return "Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto"

    if "mercury" in text:
        return "Mercury is the closest planet to the Sun."

    if "venus" in text:
        return "Venus is the hottest planet in the solar system."

    if "earth" in text:
        return "Earth is our home planet."

    if "mars" in text:
        return "Mars is the Red Planet."

    if "jupiter" in text:
        return "Jupiter is the largest planet."

    if "saturn" in text:
        return "Saturn has rings."

    # COUNTRIES
    if "capital of liberia" in text:
        return "Monrovia"

    if "capital of nigeria" in text:
        return "Abuja"

    if "capital of ghana" in text:
        return "Accra"

    # GRAMMAR
    if "noun" in text:
        return "A noun is a naming word."

    if "verb" in text:
        return "A verb is an action word."

    return None


# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    global memory

    user_message = request.json.get("message", "")
    text = user_message.lower().strip()

    # =========================
    # CHAT LOG
    # =========================
    memory["chat_history"].append(user_message)
    memory["chat_history"] = memory["chat_history"][-20:]
    save_memory(memory)

    # =========================
    # 1. SELF LEARNING FIRST
    # =========================
    learned = learn_system(user_message, memory)
    if learned:
        return jsonify({"response": learned})

    # =========================
    # 2. BRAIN
    # =========================
    smart = brain(user_message, memory)
    if smart:
        return jsonify({"response": smart})

    # =========================
    # 3. KNOWLEDGE ENGINE
    # =========================
    knowledge_response = knowledge(user_message)
    if knowledge_response:
        return jsonify({"response": knowledge_response})

    # =========================
    # 4. MEMORY ACTIONS
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
    # DEFAULT
    # =========================
    return jsonify({
        "response": "ScienX AI received your message. Try asking science, geography, or teach me something."
    })


# =========================
# RUN (RENDER SAFE)
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
