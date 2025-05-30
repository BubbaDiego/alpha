# GPT Personas

This file documents the persona system used by the GPT Oracle routes. Personas control the tone and framing of responses without modifying the underlying data.

## Available Personas

- `default` – neutral assistant replies
- `gothic` – mystical, archaic language
- `surfer` – laid-back surfer slang

## API Usage

Send a `persona` query parameter with `/gpt/oracle/<topic>` or use the dedicated route:

```bash
curl "http://localhost:5000/gpt/persona/gothic/portfolio?strategy=degen"
```

The topic can be `portfolio`, `alerts`, `prices` or `system`. Combine `persona` with a `strategy` to adjust risk guidance.
