const elements = {
  form: document.querySelector("#noticeForm"),
  text: document.querySelector("#noticeText"),
  image: document.querySelector("#imageInput"),
  preview: document.querySelector("#imagePreview"),
  removeImage: document.querySelector("#removeImage"),
  dropZone: document.querySelector("#dropZone"),
  charCount: document.querySelector("#charCount"),
  button: document.querySelector("#analyzeButton"),
  resetButton: document.querySelector("#resetButton"),
  error: document.querySelector("#formError"),
  status: document.querySelector("#modelStatus"),
  results: document.querySelector("#results"),
  risk: document.querySelector("#riskBadge"),
  source: document.querySelector("#resultSource"),
  uploadHint: document.querySelector("#uploadHint"),
  textHint: document.querySelector("#textHint"),
  saveTrace: document.querySelector("#saveTrace"),
};

let imageDataUrl = "";
let activeMode = null;
let activeExampleId = "";

async function callGradioApi(name, data) {
  const response = await fetch(`/gradio_api/call/${name}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data }),
  });
  if (!response.ok) throw new Error("The app could not start the request.");
  const { event_id: eventId } = await response.json();
  const stream = await fetch(`/gradio_api/call/${name}/${eventId}`);
  if (!stream.ok || !stream.body) throw new Error("The app could not read the result.");

  const reader = stream.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() || "";
    for (const chunk of chunks) {
      const event = chunk.match(/^event:\s*(.+)$/m)?.[1];
      const raw = chunk.match(/^data:\s*(.+)$/m)?.[1];
      if (event === "error") throw new Error("The request could not be completed.");
      if (event === "complete" && raw) {
        const values = JSON.parse(raw);
        return values[0];
      }
    }
  }
  throw new Error("The app returned no result.");
}

function setStatus(status) {
  if (!status) return;
  elements.status.lastChild.textContent = status.label || "Modal model unavailable";
  elements.status.classList.toggle("connected", Boolean(status.connected));
}

async function loadStatus() {
  try {
    setStatus(await callGradioApi("status", []));
  } catch {
    setStatus({ connected: false, label: "Modal model unavailable" });
  }
}

function showError(message = "") {
  elements.error.textContent = message;
  elements.error.classList.toggle("visible", Boolean(message));
}

function setMode(mode) {
  activeMode = mode;
  const isImage = mode === "image";
  const isText = mode === "text";

  elements.text.disabled = isImage;
  elements.dropZone.classList.toggle("disabled", isText);
  elements.image.disabled = isText;

  elements.uploadHint.classList.toggle("visible", isImage);
  elements.textHint.classList.toggle("visible", isText);
  elements.resetButton.classList.toggle("visible", Boolean(mode));
}

function setLoading(loading) {
  elements.button.disabled = loading;
  elements.button.classList.toggle("loading", loading);
  elements.button.querySelector(".button-label").textContent =
    loading ? "Checking safely..." : "Check this notice";
}

function renderList(selector, items) {
  const list = document.querySelector(selector);
  list.replaceChildren(...items.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));
}

function renderResult(payload) {
  if (!payload.ok) throw new Error(payload.error || "Unable to analyze this input.");
  const result = payload.assessment;
  setStatus(payload.status);
  elements.risk.className = `risk-badge risk-${result.risk_label.toLowerCase().replaceAll(" ", "-")}`;
  elements.risk.textContent = result.risk_label;
  document.querySelector("#explanationText").textContent = result.simple_explanation;
  renderList("#redFlagsList", result.red_flags);
  renderList("#nextStepsList", result.safe_next_steps);

  const replyCard = document.querySelector("#replyCard");
  const replyText = document.querySelector("#replyText");
  const replyAllowed = ["Verify first", "Suspicious"].includes(result.risk_label);
  if (replyAllowed && result.reply_draft && result.reply_draft.trim()) {
    replyText.textContent = result.reply_draft;
    replyCard.hidden = false;
  } else {
    replyCard.hidden = true;
  }

  elements.source.textContent = payload.source === "model"
    ? "Analyzed by the deployed Qwen model endpoint."
    : payload.source === "cached_modal_example"
      ? "Cached Modal result"
      : "";
  elements.source.classList.toggle(
    "cached-result",
    payload.source === "cached_modal_example",
  );
  elements.results.hidden = false;
  elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function useImage(file) {
  if (!file) return;
  activeExampleId = "";
  const allowed = ["image/png", "image/jpeg", "image/webp"];
  if (!allowed.includes(file.type)) return showError("Use a PNG, JPG, or WebP image.");
  if (file.size > 8 * 1024 * 1024) return showError("Please choose an image smaller than 8 MB.");
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    imageDataUrl = String(reader.result);
    elements.preview.src = imageDataUrl;
    elements.dropZone.classList.add("has-image");
    showError();
    setMode("image");
  });
  reader.readAsDataURL(file);
}

elements.image.addEventListener("change", () => useImage(elements.image.files[0]));
elements.removeImage.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  imageDataUrl = "";
  activeExampleId = "";
  elements.image.value = "";
  elements.preview.removeAttribute("src");
  elements.dropZone.classList.remove("has-image");
  setMode(null);
});
["dragenter", "dragover"].forEach((name) => elements.dropZone.addEventListener(name, (event) => {
  event.preventDefault();
  elements.dropZone.classList.add("dragging");
}));
["dragleave", "drop"].forEach((name) => elements.dropZone.addEventListener(name, (event) => {
  event.preventDefault();
  elements.dropZone.classList.remove("dragging");
}));
elements.dropZone.addEventListener("drop", (event) => useImage(event.dataTransfer.files[0]));
elements.text.addEventListener("input", () => {
  activeExampleId = "";
  elements.charCount.textContent = `${elements.text.value.length.toLocaleString()} / 12,000`;
  if (elements.text.value.trim().length === 1) {
    setMode("text");
  }
  if (elements.text.value.trim().length === 0 && activeMode === "text") {
    setMode(null);
  }
});

document.querySelectorAll(".example-card").forEach((button) => {
  button.addEventListener("click", async () => {
    if (button.dataset.image) {
      try {
        const response = await fetch(button.dataset.image);
        const blob = await response.blob();
        const reader = new FileReader();
        reader.addEventListener("load", () => {
          imageDataUrl = String(reader.result);
          activeExampleId = button.dataset.exampleId || "";
          elements.preview.src = imageDataUrl;
          elements.dropZone.classList.add("has-image");
          showError();
          setMode("image");
          document.querySelector(".workspace").scrollIntoView({ behavior: "smooth" });
        });
        reader.readAsDataURL(blob);
      } catch {
        showError("Could not load the example image.");
      }
    } else if (button.dataset.example) {
      elements.text.value = button.dataset.example;
      elements.text.dispatchEvent(new Event("input"));
      activeExampleId = button.dataset.exampleId || "";
      elements.text.focus();
      setMode("text");
      document.querySelector(".workspace").scrollIntoView({ behavior: "smooth" });
    }
  });
});

elements.resetButton.addEventListener("click", () => {
  imageDataUrl = "";
  activeExampleId = "";
  elements.image.value = "";
  elements.preview.removeAttribute("src");
  elements.dropZone.classList.remove("has-image");
  elements.text.value = "";
  elements.charCount.textContent = "0 / 12,000";
  elements.results.hidden = true;
  showError();
  setMode(null);
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showError();
  if (!elements.text.value.trim() && !imageDataUrl) {
    return showError("Paste a message or upload a screenshot to continue.");
  }

  if (activeMode === "image") {
    elements.text.value = "";
    elements.charCount.textContent = "0 / 12,000";
  } else if (activeMode === "text") {
    imageDataUrl = "";
    elements.image.value = "";
    elements.preview.removeAttribute("src");
    elements.dropZone.classList.remove("has-image");
  }

  setLoading(true);
  try {
    const submittedImage = activeExampleId ? "" : imageDataUrl;
    renderResult(await callGradioApi(
      "analyze",
      [elements.text.value, submittedImage, activeExampleId, elements.saveTrace.checked],
    ));
  } catch (error) {
    showError(error.message || "The request could not be completed.");
  } finally {
    setLoading(false);
  }
});

document.querySelectorAll(".copy-button").forEach((button) => {
  button.addEventListener("click", async () => {
    const target = document.querySelector(`#${button.dataset.copy}`);
    await navigator.clipboard.writeText(target.innerText);
    const original = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = original; }, 1200);
  });
});

loadStatus();
