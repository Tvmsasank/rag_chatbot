let waitingForConfirmation = false;

/* =========================
   CHAT OPEN / CLOSE
========================= */

function toggleChat() {

  let chat = document.getElementById("chatWindow");

  if (chat.style.display === "flex") {
    chat.style.display = "none";
  } else {
    chat.style.display = "flex";
  }
}

/* =========================
   ADD MESSAGE
========================= */

function addMessage(text, type) {

  let chat = document.getElementById("chat");

  let div = document.createElement("div");

  div.className = "msg " + type;

  div.innerHTML = text;

  chat.appendChild(div);

  chat.scrollTop = chat.scrollHeight;
}

/* =========================
   RESET CHAT
========================= */

function resetChat() {

  let chat = document.getElementById("chat");

  waitingForConfirmation = false;

  chat.innerHTML = `

    <div class="msg bot">
      👋 Welcome to University AI Assistant.
      <br><br>

      I can help you with:
      <br><br>

      • Fees Due<br>
      • Attendance<br>
      • Exam Results<br>
      • Assignments<br>
      • Scholarship Status<br>
      • Library Details
    </div>

    <div class="quick-actions">

      <button onclick="quickAsk('Check my fees due')">
        💰 Fees
      </button>

      <button onclick="quickAsk('Show my attendance')">
        📊 Attendance
      </button>

      <button onclick="quickAsk('Show my exam result')">
        📝 Results
      </button>

      <button onclick="quickAsk('Show my assignments')">
        📚 Assignments
      </button>

      <button onclick="quickAsk('Show my scholarship status')">
        🎓 Scholarship
      </button>

      <button onclick="quickAsk('Show my library books')">
        📖 Library
      </button>

    </div>
  `;
}

/* =========================
   QUICK ASK
========================= */

function quickAsk(text) {

  document.getElementById("q").value = text;

  ask();
}

/* =========================
   END CONVERSATION
========================= */

function endConversation() {

  addMessage(
    `
    ❤️ Thank you for using University AI Assistant.
    <br><br>

    For your privacy and security,
    this conversation will now be cleared.
    `,
    "bot"
  );

  setTimeout(() => {

    resetChat();

  }, 3500);
}

/* =========================
   MAIN ASK FUNCTION
========================= */

async function ask() {

  let input = document.getElementById("q");

  let q = input.value.trim();

  if (q === "") return;

  input.value = "";

  addMessage(q, "user");

  let lower = q.toLowerCase().trim();

  /* =========================
     THANK YOU FLOW
  ========================= */

  let thanksWords = [
    "thanks",
    "thank you",
    "ok thanks",
    "okay thanks",
    "bye",
    "goodbye",
    "done",
    "thats all",
    "that's all",
    "no thanks"
  ];

  if (thanksWords.includes(lower)) {

    endConversation();

    return;
  }

  /* =========================
     YES / NO FLOW
  ========================= */

  if (waitingForConfirmation) {

    if (lower === "yes") {

      waitingForConfirmation = false;

      addMessage(
        `
        😊 Great!

        <br><br>

        Please ask your next question.
        `,
        "bot"
      );

      return;
    }

    if (lower === "no") {

      waitingForConfirmation = false;

      endConversation();

      return;
    }

    addMessage(
      `
      Please type:
      <br><br>

      ✅ YES — continue chatting
      <br>
      ❌ NO — end conversation
      `,
      "bot"
    );

    return;
  }

  /* =========================
     TYPING
  ========================= */

  let chat = document.getElementById("chat");

  let typing = document.createElement("div");

  typing.className = "msg bot";

  typing.id = "typing";

  typing.innerHTML = "Typing...";

  chat.appendChild(typing);

  chat.scrollTop = chat.scrollHeight;

  /* =========================
     API CALL
  ========================= */

  try {

    let res = await fetch(
      "http://127.0.0.1:8000/chat?q=" +
      encodeURIComponent(q)
    );

    let data = await res.json();

    let typingEl = document.getElementById("typing");

    if (typingEl) {
      typingEl.remove();
    }

    addMessage(data.answer, "bot");

/* =========================
   ASK FOLLOWUP ONLY
   AFTER FINAL ANSWERS
========================= */

let answer = data.answer.toLowerCase();

let shouldAskConfirmation =
    answer.includes("fees due") ||
    answer.includes("attendance") ||
    answer.includes("cgpa") ||
    answer.includes("assignments") ||
    answer.includes("scholarship") ||
    answer.includes("library") ||
    answer.includes("student name");

    /* ONLY AFTER FINAL RESULT */
    if (shouldAskConfirmation) {

        setTimeout(() => {

          addMessage(
            `
            Is there anything else you want help with?
            <br><br>

            Type:
            <br><br>

            ✅ YES — continue chatting
            <br>
            ❌ NO — end conversation
            `,
            "bot"
          );

          waitingForConfirmation = true;

        }, 800);
    }
  }

  catch (err) {

    let typingEl = document.getElementById("typing");

    if (typingEl) {
      typingEl.remove();
    }

    addMessage(
      "⚠️ Server error. Please try again.",
      "bot"
    );
  }
}

/* =========================
   ENTER KEY
========================= */

function handleKey(event) {

  if (event.key === "Enter") {

    ask();
  }
}

/* =========================
   INITIAL LOAD
========================= */

resetChat();