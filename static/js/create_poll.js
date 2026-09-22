const MIN_OPTIONS = 2;
const MAX_OPTIONS = 5;

const optionList = document.getElementById("option-list");
const addButton = document.getElementById("add-option");

function wireCharCounter(input, counter) {
  const update = () => {
    const max = input.maxLength;
    const length = input.value.length;
    counter.textContent = `${length}/${max}`;
    counter.classList.toggle("char-counter-warning", length >= max * 0.9);
  };
  input.addEventListener("input", update);
  update();
}

function makeOptionRow(index) {
  const row = document.createElement("div");
  row.className = "option-row";
  row.innerHTML = `
    <div class="option-row-fields">
      <input type="text" name="option" maxlength="100" placeholder="Seçenek ${index}">
      <button type="button" class="option-remove" aria-label="Seçeneği sil">×</button>
    </div>
    <span class="char-counter"></span>
  `;
  wireCharCounter(row.querySelector("input"), row.querySelector(".char-counter"));
  return row;
}

function updateRowState() {
  const rows = optionList.querySelectorAll(".option-row");
  rows.forEach((row, i) => {
    const removeBtn = row.querySelector(".option-remove");
    removeBtn.style.display = rows.length > MIN_OPTIONS ? "inline-flex" : "none";
    row.querySelector("input").placeholder = `Seçenek ${i + 1}`;
  });
  addButton.disabled = rows.length >= MAX_OPTIONS;
}

if (optionList && addButton) {
  optionList.querySelectorAll(".option-row").forEach((row) => {
    wireCharCounter(row.querySelector("input"), row.querySelector(".char-counter"));
  });

  addButton.addEventListener("click", () => {
    const count = optionList.querySelectorAll(".option-row").length;
    if (count >= MAX_OPTIONS) return;
    optionList.appendChild(makeOptionRow(count + 1));
    updateRowState();
  });

  optionList.addEventListener("click", (event) => {
    if (!event.target.classList.contains("option-remove")) return;
    const rows = optionList.querySelectorAll(".option-row");
    if (rows.length <= MIN_OPTIONS) return;
    event.target.closest(".option-row").remove();
    updateRowState();
  });

  updateRowState();
}

const questionInput = document.getElementById("id_question");
const questionCounter = document.querySelector('[data-counter-for="id_question"]');
if (questionInput && questionCounter) {
  wireCharCounter(questionInput, questionCounter);
}
