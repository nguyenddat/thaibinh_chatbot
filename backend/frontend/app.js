import { marked } from "https://cdn.jsdelivr.net/npm/marked@11.1.1/lib/marked.esm.js";

const chatWindow = document.querySelector("#chat-window");
const form = document.querySelector("form");
const questionInput = document.querySelector("textarea");
const submitBtn = document.querySelector("button[type='submit']");
const clearBtn = document.querySelector("#clear-history");

const API_BASE = `${window.location.origin}/api/chat`;
const state = {
  history: [],
};

const ROLE_LABEL = {
  user: "Bạn",
  ai: "Trợ lý",
  system: "Hệ thống",
};

// MARKED CONFIG
marked.setOptions({
  gfm: true,
  breaks: true,
});

/* -----------------------------------------------------
   FIX MARKDOWN
------------------------------------------------------- */
function normalizeMarkdown(text = "") {
  if (!text) return "";
  let normalized = text;

  // Fix API returning literal "\n"
  normalized = normalized.replace(/\\n/g, "\n");

  return normalized.trim();
}

/* -----------------------------------------------------
   RENDER MARKDOWN
------------------------------------------------------- */
function renderMarkdown(text = "") {
  const clean = normalizeMarkdown(text);
  const purifier = window?.DOMPurify;
  const html = marked.parse(clean);
  return purifier ? purifier.sanitize(html) : html;
}

/* -----------------------------------------------------
   APPEND MESSAGE
------------------------------------------------------- */
function appendMessage(role, message, recommendations = []) {
  const article = document.createElement("article");
  article.className = `chat-bubble ${role}`;

  // Role Label
  const roleSpan = document.createElement("div");
  roleSpan.className = "role";
  roleSpan.textContent = ROLE_LABEL[role] || role;
  article.appendChild(roleSpan);

  // Message Content
  const messageDiv = document.createElement("div");
  messageDiv.className = "message-content";
  messageDiv.innerHTML = renderMarkdown(message);
  article.appendChild(messageDiv);

  // Recommendations (Only for AI)
  if (recommendations && recommendations.length > 0 && role === 'ai') {
    const recContainer = document.createElement("div");
    recContainer.className = "recommendations-container";

    const recLabel = document.createElement("span");
    recLabel.className = "recommendations-label";
    recLabel.textContent = "Gợi ý câu hỏi tiếp theo:";
    recContainer.appendChild(recLabel);

    const chipsDiv = document.createElement("div");
    chipsDiv.className = "recommendation-chips";

    recommendations.forEach(text => {
      const chip = document.createElement("button");
      chip.className = "recommendation-chip";
      chip.textContent = text;
      chip.type = "button";
      chip.addEventListener("click", () => {
        questionInput.value = text;
        questionInput.focus();
        // Optional: Auto-submit
        // form.dispatchEvent(new Event('submit')); 
      });
      chipsDiv.appendChild(chip);
    });

    recContainer.appendChild(chipsDiv);
    article.appendChild(recContainer);
  }

  chatWindow.appendChild(article);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/* -----------------------------------------------------
   LOADING UI
------------------------------------------------------- */
function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.textContent = isLoading ? "..." : "Gửi";
}

/* -----------------------------------------------------
   POST JSON
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
   CHAT PIPELINE
------------------------------------------------------- */
async function runPipeline(question) {
  const trimmedHistory = state.history.slice(-6);

  // 1. Guardrail
  const guardrail = await postJSON(`${API_BASE}/guardrail`, { question });
  if (!guardrail.verified) throw new Error("Câu hỏi chưa hợp lệ, vui lòng diễn đạt lại.");

  // 2. Analysis
  const analysis = await postJSON(`${API_BASE}/analysis`, {
    question,
    chat_history: trimmedHistory,
  });

  const payload = {
    question,
    intent: analysis.intent ?? "welcome",
    tasks: analysis.tasks?.length ? analysis.tasks : undefined,
    analysis_method: analysis.analysis_method,
    analysis_params: analysis.analysis_params,
  };

  // 3. Chat Response
  const chatResponse = await postJSON(API_BASE + "/", payload);
  const output = chatResponse.output?.response?.[0];

  return {
    answer: output?.content ?? "Hệ thống chưa có phản hồi.",
    recommendations: analysis.recommendations ?? output?.recommendations ?? [],
  };
}

/* -----------------------------------------------------
   FORM SUBMIT
------------------------------------------------------- */
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  appendMessage("user", question);
  questionInput.value = "";
  setLoading(true);

  try {
    const { answer, recommendations } = await runPipeline(question);
    appendMessage("ai", answer, recommendations);
    state.history.push({ human: question }, { ai: answer });
  } catch (err) {
    appendMessage("system", `Lỗi: ${err.message}`);
  } finally {
    setLoading(false);
  }
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
   INITIAL GREETING
------------------------------------------------------- */
appendMessage(
  "ai",
  "Xin chào! Tôi có thể giúp bạn tra cứu và tóm tắt các thủ tục hành chính tại Thái Bình. Hãy đặt câu hỏi để bắt đầu nhé.",
  ["Thủ tục đăng ký khai sinh", "Làm thẻ căn cước công dân", "Đăng ký kết hôn"]
);