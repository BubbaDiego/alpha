const AVATARS = {
  "Fox": {
    icon: "🦊",
    moods: { calm: "🌿", neutral: "😐", chaotic: "💥" },
    heat: "🔥"
  },
  "Rocket": {
    icon: "🚀",
    moods: { calm: "🧊", neutral: "🛰️", chaotic: "🚨" },
    heat: "🌡️"
  },
  "Panther": {
    icon: "🐆",
    moods: { calm: "🍃", neutral: "🕶️", chaotic: "⚡" },
    heat: "🌋"
  },
  "R2": {
    icon: "/static/images/r2d2_icon.jpg",
    moods: { calm: "🎵", neutral: "🤖", chaotic: "🔊" },
    heat: "📟"
  },
  "C3P0": {
    icon: "/static/images/c3po_icon.jpg",
    moods: { calm: "🤖", neutral: "💬", chaotic: "😰" },
    heat: "⚙️"
  },

  "Jabba": {
    icon: "/static/images/jabba_icon.jpg",
    moods: { calm: "😋", neutral: "👑", chaotic: "🧨" },
    heat: "🌋"
  },
  "Chewbacca": {
    icon: "/static/images/chewie_icon.jpg",
    moods: { calm: "🐻", neutral: "⚒️", chaotic: "🗯️" },
    heat: "🔊"
  },
  "Palpatine": {
    icon: "/static/images/palpatine_icon.jpg",
    moods: { calm: "😈", neutral: "⚡", chaotic: "👿" },
    heat: "🌩️"
  },
  "Luke": {
    icon: "/static/images/luke_icon.jpg",
    moods: { calm: "🧘", neutral: "💫", chaotic: "⚔️" },
    heat: "✨"
  },

  "Lando": {
    icon: "/static/images/lando_icon.jpg",
    moods: { calm: "🧘", neutral: "🎯", chaotic: "🎲" },
    heat: "🔥"
  },
  "Vader": {
    icon: "/static/images/vader_icon.jpg",
    moods: { calm: "🕳️", neutral: "🛡️", chaotic: "☠️" },
    heat: "💀"
  },
  "Yoda": {
    icon: "/static/images/yoda_icon.jpg",
    moods: { calm: "🌱", neutral: "🧘", chaotic: "⚔️" },
    heat: "✨"
  },
  "Boba": {
    icon: "/static/images/boba_icon.jpg",
    moods: { calm: "🎯", neutral: "🤠", chaotic: "💣" },
    heat: "🚀"

  },
  "Leia": {
    icon: "/static/images/leia_icon.jpg",
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
    .then(res => {
      if (!res.ok) {
        return res.text().then(text => {
          throw new Error(`HTTP ${res.status}: ${text.slice(0, 60)}`);
        });
      }
      const ct = res.headers.get('content-type') || '';
      if (!ct.includes('application/json')) {
        return res.text().then(text => {
          throw new Error(`Non-JSON response: ${text.slice(0, 60)}`);
        });
      }
      return res.json();
    })
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

          let avatarHTML = '';
          if (trader.avatar?.startsWith('/static/')) {
            avatarHTML = `<img src="${trader.avatar}" class="leader-avatar">`;
          } else if (trader.avatar) {
            avatarHTML = `<span class="leader-avatar">${trader.avatar}</span>`;
          }

          const avatarKey = getAvatarKey(trader.avatar);
          const moodIcon = AVATARS[avatarKey]?.moods?.[trader.mood] ?? '';

          row.innerHTML = `
            <td>${avatarHTML}</td>
            <td>${trader.name}</td>
            <td>${trader.performance_score ?? '?'}</td>
            <td>$${trader.wallet_balance?.toFixed(2) ?? '0.00'}</td>
            <td>$${trader.profit?.toFixed(2) ?? '0.00'}</td>
            <td>${trader.heat_index?.toFixed(1) ?? 'N/A'}</td>
            <td>${moodIcon} ${trader.mood}</td>
          `;
          leaderboard.appendChild(row);
        }
      });

      if (leaderboard) {
        const footer = document.getElementById('leaderboard-footer');
        if (footer) footer.innerHTML = '';

        const count = sorted.length;
        const totalScore = sorted.reduce((sum, t) => sum + (t.performance_score ?? 0), 0);
        const totalBalance = sorted.reduce((sum, t) => sum + (t.wallet_balance ?? 0), 0);
        const totalProfit = sorted.reduce((sum, t) => sum + (t.profit ?? 0), 0);
        const totalHeat = sorted.reduce((sum, t) => sum + (t.heat_index ?? 0), 0);

        const avgScore = count ? (totalScore / count) : 0;
        const avgHeat = count ? (totalHeat / count) : 0;

        const row = document.createElement('tr');
        row.classList.add('leader-total-row');
        row.innerHTML = `
          <td></td>
          <td></td>
          <td>${avgScore.toFixed(2)}</td>
          <td>$${totalBalance.toFixed(2)}</td>
          <td>$${totalProfit.toFixed(2)}</td>
          <td>${avgHeat.toFixed(1)}</td>
          <td></td>
        `;
        if (footer) footer.appendChild(row);
      }

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
              <p>Profit: $${trader.profit?.toFixed(2) ?? '0.00'}</p>
            </div>
            <div class="card-back">
              <p>Score: ${trader.performance_score ?? "?"}</p>
              <p>Strategy Count: ${Object.keys(trader.strategies || {}).length}</p>
              <p>Born on: ${trader.born_on ? new Date(trader.born_on).toLocaleString() : 'N/A'}</p>
              <p>Initial Collateral: $${(trader.initial_collateral ?? 0).toFixed(2)}</p>
              <p class="pub-address">${trader.public_address ?? 'N/A'}</p>
              <button class="btn btn-danger btn-sm mt-2" onclick="deleteTrader('${trader.name}')">Delete</button>
            </div>
          </div>
        `;
container.appendChild(card);
      });
    })
    .catch(err => {
      console.error("\u274c Failed to load traders:", err);
      alert("\u274c Error loading traders.");
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

function createStarWarsTraders() {
  if (!confirm("Create Star Wars traders?")) return;
  fetch('/trader/api/traders/create_star_wars', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('✅ Star Wars traders created!');
        location.reload();
      } else {
        alert('❌ Failed to create traders.');
      }
    })
    .catch(err => {
      console.error('create star wars traders failed', err);
      alert('❌ Error creating traders.');
    });
}

function deleteAllTraders() {
  if (!confirm('Delete ALL traders?')) return;
  fetch('/trader/api/traders/delete_all', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('🧹 All traders deleted.');
        location.reload();
      } else {
        alert('❌ Failed to delete traders.');
      }
    })
    .catch(err => {
      console.error('delete all traders failed', err);
      alert('❌ Error deleting traders.');
    });
}

document.addEventListener('DOMContentLoaded', () => {
  loadAvatars();
  loadWallets();
  loadTraders();
  document.getElementById('starWarsBtn')?.addEventListener('click', createStarWarsTraders);
  document.getElementById('deleteAllTradersBtn')?.addEventListener('click', deleteAllTraders);
});
