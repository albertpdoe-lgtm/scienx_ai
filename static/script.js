const orb = document.getElementById("orb");
const orbStatus = document.getElementById("orbStatus");
const messages = document.getElementById("messages");
const chatList = document.getElementById("chatList");
const inputBox = document.getElementById("userInput");

let voiceActive = false;
let wakeWordMode = true;
let recognition;

let mathMode = false;
let scienceMode = false;

let chats = JSON.parse(localStorage.getItem("scienx_chats") || "[]");
let activeChatId = null;

let contextMemory = [];

/* =========================
   WAKE WORD ENGINE (STABLE)
========================= */
function handleWakeWord(text){

    const msg = text.toLowerCase().trim();

    if(msg.includes("hey scienx") || msg.includes("hi scienx")){

        if(voiceActive) return true; // 🔥 prevents spam trigger

        voiceActive = true;

        orb.classList.add("active");
        orbStatus.innerText = "SCIENX ACTIVATED 🎤";

        speak("Yes? I'm listening");

        try{
            recognition.start();
        }catch(e){}

        return true;
    }

    return false;
}

/* =========================
   MATH MODE
========================= */
function toggleMathMode(){

    mathMode = !mathMode;
    scienceMode = false;

    orbStatus.innerText = mathMode
        ? "MATH MODE ACTIVE 🧮"
        : "SCIENX CORE ONLINE";

    messages.innerHTML += `
        <div class="bot">
            ${mathMode ? "🧮 Math Engine Activated" : "🧠 Normal Mode Activated"}
        </div>
    `;

    scrollChat();
}

/* =========================
   SCIENCE MODE
========================= */
function toggleScienceMode(){

    scienceMode = !scienceMode;
    mathMode = false;

    orbStatus.innerText = scienceMode
        ? "SCIENCE MODE ACTIVE 🔬"
        : "SCIENX CORE ONLINE";

    messages.innerHTML += `
        <div class="bot">
            ${scienceMode ? "🔬 Science Mode Activated" : "🧠 Science Mode Disabled"}
        </div>
    `;

    scrollChat();
}

/* =========================
   CHAT SYSTEM
========================= */
function newChat(){

    const id = Date.now().toString();

    const chat = {
        id,
        title: "New Chat",
        messages: []
    };

    chats.unshift(chat);
    activeChatId = id;

    saveChats();
    renderChatList();

    messages.innerHTML = "";
}

function saveChats(){
    localStorage.setItem("scienx_chats", JSON.stringify(chats));
}

function renderChatList(){

    if(!chatList) return;

    chatList.innerHTML = "";

    chats.forEach(chat => {

        const li = document.createElement("li");
        li.textContent = chat.title;

        li.onclick = () => loadChat(chat.id);

        if(chat.id === activeChatId){
            li.style.background = "rgba(0,255,255,0.15)";
        }

        chatList.appendChild(li);
    });
}

function loadChat(id){

    const chat = chats.find(c => c.id === id);
    if(!chat) return;

    activeChatId = id;
    messages.innerHTML = "";

    chat.messages.forEach(m => {
        messages.innerHTML += `
            <div class="user">${m.user}</div>
            <div class="bot">${m.bot}</div>
        `;
    });

    scrollChat();
    renderChatList();
}

function saveMessage(user, bot){

    let chat = chats.find(c => c.id === activeChatId);

    if(!chat){
        newChat();
        chat = chats[0];
    }

    chat.messages.push({user, bot});

    if(chat.messages.length === 1){
        chat.title = user.slice(0, 25);
    }

    saveChats();
    renderChatList();
}

/* =========================
   SEND MESSAGE
========================= */
async function sendMessage(messageFromVoice = null){

    const text = messageFromVoice || inputBox.value.trim();
    if(text === "") return;

    inputBox.value = "";

    contextMemory.push(text);
    if(contextMemory.length > 10){
        contextMemory.shift();
    }

    /* =========================
       MATH MODE
    ========================= */
    if(mathMode){

        try{
            const result = eval(text);
            const reply = `The answer is ${result}`;

            messages.innerHTML += `
                <div class="user">${text}</div>
                <div class="bot">${reply}</div>
            `;

            saveMessage(text, reply);
            scrollChat();

            if(voiceActive) speak(reply);
            return;

        } catch(e){

            const reply = "Unable to solve expression";

            messages.innerHTML += `
                <div class="bot">${reply}</div>
            `;

            scrollChat();

            if(voiceActive) speak(reply);
            return;
        }
    }

    /* =========================
       NORMAL CHAT
    ========================= */

    messages.innerHTML += `<div class="user">${text}</div>`;

    orb.classList.add("thinking");
    orbStatus.innerText = "SCIENX THINKING...";

    const response = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text})
    });

    const data = await response.json();

    messages.innerHTML += `<div class="bot">${data.response}</div>`;

    saveMessage(text, data.response);
    scrollChat();

    orb.classList.remove("thinking");
    orbStatus.innerText = voiceActive ? "VOICE ACTIVE 🎤" : "READY";

    if(voiceActive) speak(data.response);
}

/* =========================
   ENTER KEY
========================= */
inputBox.addEventListener("keypress", function(event){
    if(event.key === "Enter"){
        sendMessage();
    }
});

/* =========================
   INIT CHAT
========================= */
window.addEventListener("load", ()=>{

    if(chats.length > 0){
        activeChatId = chats[0].id;
        loadChat(activeChatId);
    } else {
        newChat();
    }

    renderChatList();
});

/* =========================
   VOICE SYSTEM (FIXED + STABLE)
========================= */
const SpeechRecognition =
window.SpeechRecognition || window.webkitSpeechRecognition;

if(SpeechRecognition){

    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;

    orb.addEventListener("click", ()=>{

        voiceActive = !voiceActive;

        if(voiceActive){
            orb.classList.add("active");
            orbStatus.innerText = "VOICE ACTIVE 🎤";

            speak("ScienX voice system activated");

            try{ recognition.start(); }catch(e){}
        } 
        else {
            orb.classList.remove("active");
            orbStatus.innerText = "VOICE STOPPED";

            speak("Voice system deactivated");

            try{ recognition.stop(); }catch(e){}
        }
    });

    recognition.onresult = (event)=>{

        const text = event.results[0][0].transcript;

        inputBox.value = text;

        if(handleWakeWord(text)) return;

        sendMessage(text);
    };

    recognition.onend = ()=>{

        if(voiceActive){
            setTimeout(()=>{
                try{
                    recognition.start();
                }catch(e){}
            }, 500);
        }
    };
}

/* =========================
   UTIL
========================= */
function scrollChat(){
    messages.scrollTop = messages.scrollHeight;
}

/* =========================
   SPEECH ENGINE (TEEN / JARVIS HYBRID)
========================= */
function speak(text){

    if(!("speechSynthesis" in window)) return;

    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = "en-US";

    // 🔥 teen + slightly AI tone
    utterance.rate = 1.0;
    utterance.pitch = 1.15;

    const voices = speechSynthesis.getVoices();

    const preferred = voices.find(v =>
        v.name.includes("Google") ||
        v.name.includes("Microsoft") ||
        v.name.includes("Zira") ||
        v.name.includes("Samantha") ||
        v.name.includes("Daniel") ||
        v.name.includes("Alex")
    );

    if(preferred){
        utterance.voice = preferred;
    }

    utterance.onstart = () => {
        orbStatus.innerText = "SCIENX SPEAKING 🔊";
    };

    utterance.onend = () => {
        orbStatus.innerText = voiceActive ? "VOICE ACTIVE 🎤" : "READY";
    };

    speechSynthesis.speak(utterance);
}

speechSynthesis.onvoiceschanged = () => {
    speechSynthesis.getVoices();
};
window.addEventListener("load", () => {

    const bootText = document.getElementById("bootText");
    const bootScreen = document.getElementById("bootScreen");

    const messages = [
        "INITIALIZING SCIENX CORE...",
        "LOADING MEMORY SYSTEM...",
        "CONNECTING VOICE ENGINE...",
        "ACTIVATING CHAT MODULE...",
        "SCIENX READY"
    ];

    let i = 0;

    const interval = setInterval(() => {

        bootText.innerText = messages[i];
        i++;

        if (i >= messages.length) {

            clearInterval(interval);

            setTimeout(() => {
                bootScreen.classList.add("fadeOut");
            }, 800);
        }

    }, 900);
});