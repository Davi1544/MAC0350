function timeAgo(dateString) {
  const now = new Date();
  const past = new Date(dateString);
  const diff = (now - past) / 1000; // seconds

  if (diff < 60) return "agora";
  if (diff < 3600) return Math.floor(diff / 60) + "m atrás";
  if (diff < 86400) return Math.floor(diff / 3600) + "h atrás";
  if (diff < 604800) return Math.floor(diff / 86400) + "d atrás";

  return Math.floor(diff / 604800) + "sem atrás";
}

function updateTimes() {
  const elements = document.querySelectorAll(".tweet-time");

  elements.forEach(el => {
    const timestamp = el.dataset.time;
    el.textContent = timeAgo(timestamp);
  });
}

updateTimes();