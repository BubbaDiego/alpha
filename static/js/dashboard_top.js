// === dashboard_top.js ===

console.log('✅ dashboard_top.js loaded');

function bindFlipCards() {
  const cards = document.querySelectorAll('.flip-card');

  cards.forEach(card => {
    // Clean up any previously attached handler
    if (card._flipHandler) {
      card.removeEventListener('click', card._flipHandler);
    }

    const handler = () => {
      card.classList.toggle('flipped');
      console.log('[Flip] Card toggled:', card);
    };

    // Store the handler reference to prevent re-binding
    card._flipHandler = handler;
    card.addEventListener('click', handler);
  });

  console.log(`🔁 Flip handlers bound to ${cards.length} cards`);
}

// Bind on page load
document.addEventListener('DOMContentLoaded', bindFlipCards);

// Optional: Rebind when content dynamically changes
const observer = new MutationObserver((mutationsList) => {
  for (const mutation of mutationsList) {
    if (mutation.addedNodes.length || mutation.removedNodes.length) {
      bindFlipCards(); // Rebind if new cards added
      break;
    }
  }
});
observer.observe(document.body, { childList: true, subtree: true });
