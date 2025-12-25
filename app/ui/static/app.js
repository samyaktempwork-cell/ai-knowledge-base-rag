const uploadBtn = document.getElementById("uploadBtn");
const askBtn = document.getElementById("askBtn");
const uploadOut = document.getElementById("uploadOut");
const answerOut = document.getElementById("answerOut");
const prettyAnswer = document.getElementById("prettyAnswer");

function setBusy(isBusy) {
  uploadBtn.disabled = isBusy;
  askBtn.disabled = isBusy;
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, m => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[m]));
}

function renderResult(data) {
  const answer = data?.answer ?? "";
  const confidence = data?.confidence ?? 0;
  const missing = data?.missing_info ?? [];
  const suggestions = data?.enrichment_suggestions ?? [];
  const citations = data?.citations ?? [];

  const confPct = Math.round(Number(confidence) * 100);

  let html = `
    <h3>Answer</h3>
    <div class="badge">Confidence: ${confPct}%</div>
    ${missing.length ? `<div class="badge">Missing info: ${missing.length}</div>` : `<div class="badge">Grounded</div>`}
    <p>${esc(answer)}</p>
  `;

  if (citations.length) {
    html += `<div class="kv"><b>Citations</b></div><ul class="list">`;
    for (const c of citations) {
      html += `<li><b>${esc(c.context_ref || "")}</b> — ${esc(c.filename || "")} (chunk ${esc(c.chunk_index)})</li>`;
    }
    html += `</ul>`;
  }

  if (missing.length) {
    html += `<div class="kv"><b>Missing info</b></div><ul class="list">`;
    for (const m of missing) html += `<li>${esc(m)}</li>`;
    html += `</ul>`;
  }

  if (suggestions.length) {
    html += `<div class="kv"><b>Enrichment suggestions</b></div><ul class="list">`;
    for (const s of suggestions) {
      html += `<li><b>${esc(s.type)}</b>: ${esc(s.suggestion)}</li>`;
    }
    html += `</ul>`;
  }

  prettyAnswer.innerHTML = html;
}

uploadBtn.onclick = async () => {
  uploadOut.textContent = "";
  const input = document.getElementById("files");

  if (!input.files.length) {
    uploadOut.textContent = "Please select file(s) first.";
    return;
  }

  setBusy(true);
  uploadOut.textContent = "Uploading...";

  try {
    const form = new FormData();
    for (const f of input.files) form.append("files", f);

    const res = await fetch("/v1/documents/upload", { method: "POST", body: form });
    const data = await res.json();
    uploadOut.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    uploadOut.textContent = `Upload failed: ${e}`;
  } finally {
    setBusy(false);
  }
};

askBtn.onclick = async () => {
  answerOut.textContent = "";
  prettyAnswer.innerHTML = "";

  const question = document.getElementById("question").value.trim();
  const top_k = Number(document.getElementById("topk").value || 6);

  if (!question) {
    prettyAnswer.innerHTML = `<p>Please enter a question.</p>`;
    return;
  }

  setBusy(true);
  prettyAnswer.innerHTML = `<p>Thinking...</p>`;

  try {
    const res = await fetch("/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k })
    });

    const data = await res.json();
    answerOut.textContent = JSON.stringify(data, null, 2);
    renderResult(data);
  } catch (e) {
    prettyAnswer.innerHTML = `<p>Query failed: ${esc(e)}</p>`;
  } finally {
    setBusy(false);
  }
};
