const AVATARS = {
  "fox": "🦊",
  "rocket": "🚀",
  "panther": "🐆",
  "r2vault": "/static/images/r2vault.jpg",
  "landovault": "/static/images/landovault.jpg",
  "vadervault": "/static/images/vadervault.jpg"
};

function loadAvatars() {
  const select = document.getElementById("avatarSelect");
  const preview = document.getElementById("avatarPreview");
  if (!select) return;

  Object.entries(AVATARS).forEach(([key, value]) => {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = key;
    select.appendChild(opt);
  });

  select.addEventListener("change", () => {
    const val = select.value;
    if (val.startsWith("/static/")) {
      preview.innerHTML = `<img src="${val}" style="height: 40px; border-radius: 50%;">`;
    } else {
      preview.innerHTML = `<span style="font-size: 1.5rem;">${val}</span>`;
    }
  });
}

function loadTraders() {
  fetch('/trader/api/traders')
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById('trader-cards');
      if (!container) return;
      container.innerHTML = "";

      if (!data.success || !Array.isArray(data.traders)) {
        container.innerHTML = "<p>No traders available.</p>";
        return;
      }

      let topScore = Math.max(...data.traders.map(t => t.performance_score ?? 0));

      data.traders.forEach(trader => {
        const card = document.createElement("div");
        card.className = "trader-card" + ((trader.performance_score ?? 0) === topScore ? " top-score" : "");

        let avatarHTML = "";
        if (trader.avatar?.startsWith("/static/")) {
          avatarHTML = `<img src="${trader.avatar}" style="height: 40px; border-radius: 50%;">`;
        } else if (trader.avatar) {
          avatarHTML = `<div style="font-size: 1.5rem;">${trader.avatar}</div>`;
        }

        card.innerHTML = `
          <div class="card-inner">
            <div class="card-front">
              <h3>${trader.name}</h3>
              ${avatarHTML}
              <p>Mood: ${trader.mood}</p>
              <p>Heat: ${trader.heat_index?.toFixed(1) ?? "N/A"}</p>
            </div>
            <div class="card-back">
              <p>Score: ${trader.performance_score ?? "?"}</p>
              <p>Strategy Count: ${Object.keys(trader.strategies || {}).length}</p>
              <button class="btn btn-danger btn-sm mt-2" onclick="deleteTrader('${trader.name}')">Delete</button>
            </div>
          </div>
        `;
        container.appendChild(card);
      });
    })
    .catch(err => {
      console.error("\u274c Failed to load traders:", err);
    });
}

function toggleTraderView() {
  const cards = document.getElementById('trader-cards');
  const formPanel = document.getElementById('trader-form-panel');
  const label = document.getElementById('toggleLabel');

  const showingForm = !formPanel.classList.contains('d-none');

  if (showingForm) {
    formPanel.classList.add('d-none');
    cards.classList.remove('d-none');
    label.textContent = 'New Trader';
  } else {
    cards.classList.add('d-none');
    formPanel.classList.remove('d-none');
    label.textContent = 'Traders';
  }
}

function cancelCreate() {
  document.getElementById('trader-form-panel').classList.add('d-none');
  document.getElementById('trader-cards').classList.remove('d-none');
}

document.getElementById("createTraderForm")?.addEventListener("submit", function(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const json = {};
  formData.forEach((value, key) => {
    json[key] = value;
  });

  fetch('/trader/api/traders/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(json)
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("\u2705 Trader created!");
      location.reload();
    } else {
      alert("\u274c Failed to create trader.");
    }
  })
  .catch(err => {
    console.error("Create trader failed:", err);
    alert("\u274c Error sending create request.");
  });
});

function deleteTrader(name) {
  if (!confirm("Delete " + name + "?")) return;

  fetch(`/trader/api/traders/${encodeURIComponent(name)}/delete`, {
    method: 'DELETE'
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("🗑️ Trader deleted.");
      location.reload();
    } else {
      alert("\u274c Failed to delete.");
    }
  })
  .catch(err => {
    console.error("Delete error:", err);
    alert("\u274c Error deleting trader.");
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadAvatars();
  loadTraders();
});
