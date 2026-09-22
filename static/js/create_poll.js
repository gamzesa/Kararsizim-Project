const MIN_OPTIONS = 2;
const MAX_OPTIONS = 5;

const optionList = document.getElementById("option-list");
const addButton = document.getElementById("add-option");

function makeOptionRow(index) {
  const row = document.createElement("div");
  row.className = "option-row";
  row.innerHTML = `
    <input type="text" name="option" maxlength="100" placeholder="Seçenek ${index}">
    <button type="button" class="option-remove" aria-label="Seçeneği sil">×</button>
  `;
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
