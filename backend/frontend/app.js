import { marked } from "https://cdn.jsdelivr.net/npm/marked@11.1.1/lib/marked.esm.js";

/* -----------------------------------------------------
   DOM
------------------------------------------------------- */
const chatWindow = document.querySelector("#chat-window");
const form = document.querySelector("#chat-form");
const questionInput = document.querySelector("#question");
const submitBtn = document.querySelector("#submit-btn");
const clearBtn = document.querySelector("#clear-history");

/* -----------------------------------------------------
   CONFIG
------------------------------------------------------- */
const API_BASE = `${window.location.origin}/api/chat`;

const state = {
  history: [],
};

const ROLE_LABEL = {
  user: "Bạn",
  ai: "Trợ lý",
  system: "Hệ thống",
};

/* -----------------------------------------------------
   MARKDOWN CONFIG
------------------------------------------------------- */
marked.setOptions({
  gfm: true,
  breaks: true,
});

/* -----------------------------------------------------
   MARKDOWN HELPERS
------------------------------------------------------- */
function normalizeMarkdown(text = "") {
  const safeText = text ? String(text) : "";
  return safeText.replace(/\\n/g, "\n").trim();
}

function renderMarkdown(text = "") {
  const clean = normalizeMarkdown(text);
  const html = marked.parse(clean);
  return window.DOMPurify ? DOMPurify.sanitize(html) : html;
}

/* -----------------------------------------------------
   UI HELPERS
------------------------------------------------------- */
function appendMessage(role, message, recommendations = []) {
  const article = document.createElement("article");
  article.className = `chat-bubble ${role}`;

  const roleDiv = document.createElement("div");
  roleDiv.className = "role";
  roleDiv.textContent = ROLE_LABEL[role] || role;

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";
  contentDiv.innerHTML = renderMarkdown(message);

  article.append(roleDiv, contentDiv);

  if (role === "ai" && recommendations.length) {
    const rec = document.createElement("div");
    rec.className = "recommendations-container";

    const label = document.createElement("span");
    label.className = "recommendations-label";
    label.textContent = "Gợi ý câu hỏi tiếp theo:";

    const chips = document.createElement("div");
    chips.className = "recommendation-chips";

    recommendations.forEach((text) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "recommendation-chip";
      btn.textContent = text;
      btn.onclick = () => {
        questionInput.value = text;
        questionInput.focus();
      };
      chips.appendChild(btn);
    });

    rec.append(label, chips);
    article.appendChild(rec);
  }

  chatWindow.appendChild(article);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setLoading(loading) {
  submitBtn.disabled = loading;
  submitBtn.textContent = loading ? "..." : "Gửi";
}

/* -----------------------------------------------------
   API
------------------------------------------------------- */
async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/* -----------------------------------------------------
   CHAT PIPELINE (SIMPLE)
------------------------------------------------------- */
async function runPipeline(question) {
  const res = await postJSON(API_BASE, {
    text: question,
    chat_history: state.history,
  });

  const output = res?.output?.response?.[0] || {};

  return {
    answer: (typeof output.content === 'string' ? output.content : JSON.stringify(output.content)) || "Hệ thống chưa có phản hồi.",
    recommendations: Array.isArray(output.recommendations) ? output.recommendations : [],
  };
}

/* -----------------------------------------------------
   ENTER TO SEND
------------------------------------------------------- */
questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

/* -----------------------------------------------------
   FORM SUBMIT
------------------------------------------------------- */
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  appendMessage("user", question);
  questionInput.value = "";
  setLoading(true);

  const { answer, recommendations } = await runPipeline(question);
  appendMessage("ai", answer, recommendations);

  state.history.push(
    { human: question },
    { ai: answer }
  );

  setLoading(false);
});

/* -----------------------------------------------------
   CLEAR HISTORY
------------------------------------------------------- */
clearBtn.addEventListener("click", () => {
  state.history = [];
  chatWindow.innerHTML = "";
  appendMessage("system", "Lịch sử đã được làm mới.");
});

/* -----------------------------------------------------
   INIT
------------------------------------------------------- */
appendMessage(
  "ai",
  "Xin chào! Tôi có thể giúp bạn tra cứu và tóm tắt các thủ tục hành chính tại Phường Trà Lý, tỉnh Hưng Yên.",
  [
    "Thủ tục đăng ký khai sinh",
    "Làm thẻ căn cước công dân",
    "Đăng ký kết hôn",
  ]
);
