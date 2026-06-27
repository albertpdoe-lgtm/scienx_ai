from flask import Flask, render_template, request, jsonify
import json
import os
import subprocess

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
        "name": None,
        "subject": None,
        "facts": []
    }


def save_memory(data):
    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=2)


memory = load_memory()

# =========================
# 🧠 INVESTOR / BRAIN MODE
# =========================

def brain(msg, memory):
    text = msg.lower().strip()

    if any(x in text for x in ["hello", "hi", "hey"]):
        return "Hello 👋 I am ScienX AI, your intelligent assistant."

    if "how are you" in text:
        return "I am fully operational and ready to assist you."

    if "who are you" in text:
        return "I am ScienX AI — an advanced educational and automation system."

    # Investor mode upgrade
    if any(x in text for x in ["investor", "minister", "governor", "hon.", "robert teah"]):
        return (
            "Good day and welcome. ScienX AI is an advanced educational intelligence system "
            "built to transform learning, science, and automation across Liberia and West Africa."
        )

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
        return "Earth is our home planet with life."

    if "mars" in text:
        return "Mars is known as the Red Planet."

    if "jupiter" in text:
        return "Jupiter is the largest planet in the solar system."

    if "saturn" in text:
        return "Saturn has beautiful rings."

    # COUNTRIES
    if "capital of liberia" in text:
        return "The capital of Liberia is Monrovia."

    if "capital of nigeria" in text:
        return "The capital of Nigeria is Abuja."

    if "capital of ghana" in text:
        return "The capital of Ghana is Accra."

    # GRAMMAR
    if "noun" in text:
        return "A noun is a naming word (person, place, thing, idea)."

    if "verb" in text:
        return "A verb is an action word."

    if "parts of speech" in text:
        return "8 Parts of Speech: Noun, Pronoun, Verb, Adjective, Adverb, Preposition, Conjunction, Interjection."

    # SCIENCE
    if "gravity" in text:
        return "Gravity is the force that pulls objects toward Earth."

    if "atom" in text:
        return "An atom is the smallest unit of matter."

    return None


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHAT ROUTE
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    global memory

    user_message = request.json.get("message", "")
    text = user_message.lower().strip()

    # 🧠 Brain first
    smart = brain(user_message, memory)
    if smart:
        return jsonify({"response": smart})

    # 🌍 Knowledge second
    knowledge_response = knowledge(user_message)
    if knowledge_response:
        return jsonify({"response": knowledge_response})

    # =========================
    # MEMORY SYSTEM
    # =========================

    if "remember that" in text:
        fact = user_message.replace("remember that", "").strip()
        memory["facts"].append(fact)
        save_memory(memory)
        return jsonify({"response": f"I will remember: {fact}"})


    if "my name is" in text:
        name = user_message.replace("my name is", "").strip()
        memory["name"] = name
        save_memory(memory)
        return jsonify({"response": f"Nice to meet you {name}."})

    # =========================
    # SYSTEM COMMANDS (SAFE VERSION)
    # =========================

    if "open notepad" in text:
        return jsonify({"response": "Notepad is only available on your local PC version of ScienX."})

    if "open calculator" in text:
        return jsonify({"response": "Calculator is only available on your local PC version of ScienX."})

    if "volume" in text:
        return jsonify({"response": "System control is disabled in cloud mode. Use local version."})

    # =========================
    # DEFAULT RESPONSE
    # =========================

    return jsonify({
        "response": "ScienX AI received your request. Try science, geography, math, or investor mode."
    })


# =========================
# RUN (RENDER SAFE)
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
