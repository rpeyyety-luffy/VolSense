// Person 1: reads prediction.json (made by Python) and fills the page.

async function loadPrediction() {
  // fetch() downloads the JSON file from our own website
  const response = await fetch("prediction.json");
  const p = await response.json();

  document.getElementById("vix").textContent = p.vix;
  document.getElementById("direction").textContent =
    p.direction === "rise" ? "VIX ↑ rise" : "VIX ↓ fall";
  document.getElementById("confidence").textContent = Math.round(p.confidence * 100) + "%";
  document.getElementById("accuracy").textContent = Math.round(p.test_accuracy * 100) + "%";
  document.getElementById("summary").textContent = p.summary;
  document.getElementById("date").textContent = p.date;
}

loadPrediction();

// TODO(Person 1): draw a VIX history chart with Chart.js
