const AVATARS = {
  "fox": {
    icon: "🦊",
    moods: { calm: "🌿", neutral: "😐", chaotic: "💥" },
    heat: "🔥"
  },
  "rocket": {
    icon: "🚀",
    moods: { calm: "🧊", neutral: "🛰️", chaotic: "🚨" },
    heat: "🌡️"
  },
  "panther": {
    icon: "🐆",
    moods: { calm: "🍃", neutral: "🕶️", chaotic: "⚡" },
    heat: "🌋"
  },
  "r2vault": {
    icon: "/static/images/r2vault.jpg",
    moods: { calm: "🎵", neutral: "🤖", chaotic: "🔊" },
    heat: "📟"
  },
  "landovault": {
    icon: "/static/images/landovault.jpg",
    moods: { calm: "🧘", neutral: "🎯", chaotic: "🎲" },
    heat: "🔥"
  },
  "vadervault": {
    icon: "/static/images/vadervault.jpg",
    moods: { calm: "🕳️", neutral: "🛡️", chaotic: "☠️" },
    heat: "💀"
  },
  "yodavault": {
    icon: "/static/images/yodavault.jpg",
    moods: { calm: "🌱", neutral: "🧘", chaotic: "⚔️" },
    heat: "✨"
  },
  "bobavault": {
    icon: "/static/images/bobavault.jpg",
    moods: { calm: "🎯", neutral: "🤠", chaotic: "💣" },
    heat: "🚀"
  },
  "leiavault": {
    icon: "/static/images/leiavault.jpg",
    moods: { calm: "🌸", neutral: "👑", chaotic: "⚡" },
    heat: "💫"
  }
};

function getAvatarKey(avatarPath) {
  return Object.entries(AVATARS).find(([_, value]) =>
    typeof value.icon === "string" && avatarPath === value.icon
  )?.[0] || Object.entries(AVATARS).find(([_, value]) =>
    typeof value.icon === "string" && avatarPath.includes(value.icon)
  )?.[0];
}

function loadAvatars() {
  const select = document.getElementById("avatarSelect");
  const preview = document.getElementById("avatarPreview");
  if (!select) return;

  Object.entries(AVATARS).forEach(([key, val]) => {
    const opt = document.createElement("option");
    opt.value = typeof val.icon === "string" ? val.icon : "";
    opt.textContent = key;
    select.appendChild(opt);
  });

  select.addEventListener("change", () => {
    const val = select.value;
    if (val.startsWith("/static/")) {
      preview.innerHTML = `<img src="${val}" class="avatar-circle">`;
    } else {
      preview.innerHTML = `<div class="avatar-circle">${val}</div>`;
    }
  });
}

function loadWallets() {
  const select = document.getElementById("walletSelect");
  if (!select) return;
  fetch('/trader/api/wallets')
    .then(res => res.json())
    .then(data => {
      if (!data.success) return;
      data.wallets.forEach(w => {
        const opt = document.createElement('option');
        opt.value = w.name;
        opt.textContent = `${w.name} ($${w.balance})`;
        select.appendChild(opt);
      });
    })
    .catch(err => console.error('wallet load failed', err));
}

function loadTraders() {
  fetch('/trader/api/traders')
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById('trader-cards');
      const leaderboard = document.getElementById('leaderboard-body');
      if (!container) return;
      container.innerHTML = "";
      if (leaderboard) leaderboard.innerHTML = "";

      if (!data.success || !Array.isArray(data.traders)) {
        container.innerHTML = "<p>No traders available.</p>";
        return;
      }


      let topScore = Math.max(...data.traders.map(t => t.performance_score ?? 0));

      // sort traders by score descending for leaderboard
      const sorted = [...data.traders].sort((a, b) => (b.performance_score ?? 0) - (a.performance_score ?? 0));

      sorted.forEach(trader => {
        if (leaderboard) {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${trader.name}</td>
            <td>${trader.performance_score ?? '?'}</td>
            <td>${trader.heat_index?.toFixed(1) ?? 'N/A'}</td>
            <td>${trader.mood}</td>
          `;
          leaderboard.appendChild(row);
        }
      });

      data.traders.forEach(trader => {
        const card = document.createElement("div");
        card.className = "trader-card" + ((trader.performance_score ?? 0) === topScore ? " top-score" : "");

        const avatarKey = getAvatarKey(trader.avatar);
        const moodIcon = AVATARS[avatarKey]?.moods?.[trader.mood] ?? "";
        const heatIcon = AVATARS[avatarKey]?.heat ?? "";

        let avatarHTML = "";
        if (trader.avatar?.startsWith("/static/")) {
          avatarHTML = `<img src="${trader.avatar}" class="avatar-circle">`;
        } else if (trader.avatar) {
          avatarHTML = `<div class="avatar-circle">${trader.avatar}</div>`;
        }

        card.innerHTML = `
          <div class="card-inner">
            <div class="card-front">
              <h3>${trader.name}</h3>
              ${avatarHTML}
              <p>Mood: ${moodIcon} ${trader.mood}</p>
              <p>Heat: ${heatIcon} ${trader.heat_index?.toFixed(1) ?? "N/A"}</p>
              <p>Balance: $${trader.wallet_balance?.toFixed(2) ?? '0.00'}</p>
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
  loadWallets();
  loadTraders();
});