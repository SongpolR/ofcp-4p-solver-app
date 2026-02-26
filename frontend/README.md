# Open Face Chinese Poker (OFCP) 4-Player Best Arrangement Solver (Web App)

A web app for **Open Face Chinese Poker (OFCP)** that lets you select **13 cards** via a card-like UI and computes the **best Top / Middle / Bottom arrangement** to maximize **estimated 4-player winrate** (vs 3 opponents), under a strict **≤ 1-minute** solver time cap.

---

## Features

- **Card picker UI** (tap/click cards to select up to 13)
- **4-player objective**: maximize estimated **unique table winrate**
- Shows best arrangement as **Top (3)** / **Middle (5)** / **Bottom (5)**
- **Reset** button to restart selection
- **Countdown timer** during solve
- Mobile-responsive UI (including very small screens `< 360px`)
- Backend solver enforces **time limit ≤ 60s** (default 55s)

---

## Tech Stack

**Backend**

- Python + FastAPI
- Solver: enumerates all valid 13-card splits (3/5/5), shortlists candidates, then estimates winrate using Monte Carlo simulation vs heuristic opponents
- Time-capped search (default 55s, max 60s)

**Frontend**

- React + Vite
- Responsive CSS, card-style components reused for picker and results

---

## Project Structure

- ofcp-solver-app/
  - backend/
    - app.py
    - solver.py
    - ofcp_core.py
    - bots_fullhand.py
    - requirements.txt
- frontend/
  - index.html
  - package.json
  - vite.config.js
  - src/
    - main.jsx
    - App.jsx
    - components/
      - CardPicker.jsx
      - PilesView.jsx
    - styles.css

---

## Quick Start

### 1) Backend (FastAPI)

```
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

**Backend health check:**

```
curl http://localhost:8000/health
```

### 2) Frontend (React + Vite)

```
cd frontend
npm install
npm run dev
```

**Open web: http://localhost:5173**

---

## How It Works

### Objective (4-player)

The solver estimates table performance in a 4-player setting:=

- Your arrangement is evaluated against 3 opponents
- Each simulation:
  1. Sample random opponent hands from remaining deck
  2. Arrange each opponent using a fast heuristic strategy
  3. Score a 4-player table using sum of pairwise heads-up OFCP scores
  4. Count a win when you are the unique highest total score

### Search Strategy

Because there are “only” **72,072** ways to split 13 cards into 3/5/5, the solver:

1. Enumerates all splits
2. Scores each split with a fast heuristic ranking
3. Keeps top K candidates (default `250`)
4. Runs Monte Carlo simulations on those candidates until time runs out

### Time Limit

- The backend enforces a time cap on solving.
- Default: `55s` (keeps safely below 1 minutes)
- Maximum allowed by API: `60s`

---

## API

`POST /solve`

Request:

```
{
  "cards": ["AS","KD","7H","3C","TC","9D","QH","6S","2D","JC","8H","5C","4S"],
  "time_limit_sec": 175.0,
  "shortlist_k": 250,
  "seed": 1
}
```

Response:

```
{
  "best": {
    "top": ["..", "..", ".."],
    "middle": ["..", "..", "..", "..", ".."],
    "bottom": ["..", "..", "..", "..", ".."]
  },
  "estimated_winrate": 0.412,
  "estimated_margin": 3.21,
  "elapsed_sec": 12.34,
  "shortlist_k": 250
}
```

Notes:

- cards must be exactly 13 unique cards.
- Card format is rank+suit:
  - Ranks: 2-9,T,J,Q,K,A
  - Suits: C,D,H,S

---

## Tips

- If you want faster solves:
  - Lower `shortlist_k` (e.g., 150)
- If you want potentially higher accuracy:
  - Increase `shortlist_k` (up to 2000) or increase Monte Carlo sims (requires code change)
- Solver result is stochastic due to Monte Carlo sampling; set seed for reproducibility.

---

## Development Notes

- CORS in backend is `allow_origins=["*"]` for development convenience.
  - Lock this down for production.
- The UI disables card selection while solving (to avoid confusing state).

---

## License

```
Copyright 2026 Songpol Rungsawang

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
