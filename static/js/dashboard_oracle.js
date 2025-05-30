// === dashboard_oracle.js ===
// Add click handlers for oracle icons on the dashboard panels

let availableVoices = [];

function populateVoices() {
  if (!window.speechSynthesis) return;
  availableVoices = speechSynthesis.getVoices();
}

document.addEventListener('DOMContentLoaded', () => {
  populateVoices();
  if (window.speechSynthesis) {
    speechSynthesis.onvoiceschanged = populateVoices;
  }
  document.querySelectorAll('.oracle-icon').forEach(icon => {
    icon.addEventListener('click', () => {
      const topic = icon.dataset.topic;
      if (!topic) return;
      fetch(`/gpt/oracle/${topic}`)
        .then(res => res.json())
        .then(data => {
          const reply = data.reply || data.error || 'No response';
          speakResponse(reply);
        })
        .catch(err => console.error('Oracle query failed:', err));
    });
  });
});

function speakResponse(text) {
  if (!window.speechSynthesis) return;
  speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.pitch = 1.1;
  utter.rate = 0.92;
  utter.volume = 1;
  const voice = availableVoices.find(v => v.name === 'Google UK English Female') ||
                availableVoices.find(v => v.lang && v.lang.startsWith('en'));
  if (voice) utter.voice = voice;
  speechSynthesis.speak(utter);
}
