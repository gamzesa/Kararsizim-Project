function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : null;
}

function animateResultBars(root = document) {
  root.querySelectorAll(".result-bar-fill[data-percent]").forEach((el) => {
    const target = `${el.dataset.percent}%`;
    setTimeout(() => {
      el.style.width = target;
    }, 20);
  });
}

document.addEventListener("submit", (event) => {
  const form = event.target;
  if (form.dataset.confirm && !window.confirm(form.dataset.confirm)) {
    event.preventDefault();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  animateResultBars();

  document.querySelectorAll(".messages li").forEach((toast) => {
    setTimeout(() => {
      toast.classList.add("toast-hide");
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });
});
