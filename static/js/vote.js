const voteForm = document.querySelector(".vote-form");

function renderResults(data) {
  const voteSection = voteForm.closest(".vote-section");
  const rowsHtml = data.results.map((r) => `
    <div class="result-row ${r.option_id === data.voted_option_id ? "result-row-voted" : ""}">
      <div class="result-row-label">
        ${r.text}
        ${r.option_id === data.voted_option_id ? '<span class="check-mark">✓</span>' : ""}
      </div>
      <div class="result-bar-track">
        <div class="result-bar-fill" style="width: ${r.percent}%"></div>
      </div>
      <div class="result-row-stats">${r.votes} oy · %${r.percent}</div>
    </div>
  `).join("");

  const resultsBlock = document.createElement("div");
  resultsBlock.className = "results";
  resultsBlock.innerHTML = rowsHtml;

  const meta = document.createElement("p");
  meta.className = "poll-card-meta";
  meta.textContent = `Toplam ${data.total_votes} oy`;

  voteSection.replaceWith(resultsBlock);
  resultsBlock.after(meta);
}

if (voteForm) {
  voteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitter = event.submitter;
    if (!submitter) return;

    const pollId = voteForm.dataset.pollId;
    const body = new URLSearchParams();
    body.set("option_id", submitter.value);

    const response = await fetch(`/anket/${pollId}/oy/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body,
    });

    const data = await response.json();
    if (data.ok) {
      renderResults(data);
    } else {
      window.alert(data.error || "Bir şeyler ters gitti.");
    }
  });
}
