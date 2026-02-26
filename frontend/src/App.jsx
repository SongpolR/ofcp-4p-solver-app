import React, { useEffect, useMemo, useRef, useState } from "react";
import CardPicker from "./components/CardPicker.jsx";
import PilesView from "./components/PilesView.jsx";

const API = "http://localhost:8000";

// Must match backend cap (<=60). We use 55 by default.
const DEFAULT_TIME_LIMIT_SEC = 55;

export default function App() {
  const [selected, setSelected] = useState([]);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // countdown
  const [timeLeft, setTimeLeft] = useState(DEFAULT_TIME_LIMIT_SEC);
  const timerRef = useRef(null);

  const canSolve = selected.length === 13 && !busy;

  const hint = useMemo(() => {
    if (selected.length < 13)
      return `Pick ${13 - selected.length} more card(s).`;
    if (selected.length === 13) return "Ready to solve.";
    return "Too many cards (max 13).";
  }, [selected.length]);

  const toggle = (c) => {
    if (busy) return; // prevent changing while running (optional)
    setError("");
    setResult(null);

    setSelected((prev) => {
      const has = prev.includes(c);
      if (has) return prev.filter((x) => x !== c);
      if (prev.length >= 13) return prev; // hard limit
      return [...prev, c];
    });
  };

  const reset = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;

    setSelected([]);
    setResult(null);
    setError("");
    setBusy(false);
    setTimeLeft(DEFAULT_TIME_LIMIT_SEC);
  };

  const startCountdown = (seconds) => {
    setTimeLeft(seconds);
    if (timerRef.current) clearInterval(timerRef.current);

    const startedAt = Date.now();
    timerRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startedAt) / 1000);
      const remaining = Math.max(0, seconds - elapsed);
      setTimeLeft(remaining);

      if (remaining <= 0) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }, 250);
  };

  const solve = async () => {
    setBusy(true);
    setError("");
    setResult(null);

    const timeLimit = DEFAULT_TIME_LIMIT_SEC;
    startCountdown(timeLimit);

    try {
      const res = await fetch(`${API}/solve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cards: selected,
          time_limit_sec: timeLimit,
          shortlist_k: 250,
          seed: 1,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.detail || "Solve failed");
      }
      setResult(data);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setBusy(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  return (
    <div className="container">
      <h1>OFCP 4-Player Best Arrangement Solver</h1>

      <div className="row">
        <div className="panel" style={{ flex: 2, minWidth: 360 }}>
          <div
            className="row"
            style={{ justifyContent: "space-between", alignItems: "center" }}
          >
            <h2>Your 13 cards</h2>
            <span className="badge">{selected.length}/13 selected</span>
          </div>

          <div
            className="row"
            style={{
              justifyContent: "space-between",
              alignItems: "center",
              padding: 4,
            }}
          >
            <div style={{ color: "#374151" }}>{hint}</div>

            {busy && (
              <div className="running">
                <span className="badge">Running</span>
                <span className="countdown">{timeLeft}s</span>
              </div>
            )}
          </div>

          <div className="picker-scroll">
            <CardPicker selected={selected} onToggle={toggle} />
          </div>

          <div className="btns">
            <button onClick={solve} disabled={!canSolve}>
              {busy ? "Thinking..." : "Find Best Hand"}
            </button>
            <button className="secondary" onClick={reset} disabled={busy}>
              Reset
            </button>
          </div>

          {error && (
            <div style={{ marginTop: 10, color: "#b91c1c" }}>{error}</div>
          )}
        </div>

        <div className="panel" style={{ flex: 1, minWidth: 320 }}>
          <h2>Best arrangement</h2>

          {!result && (
            <div style={{ color: "#6b7280" }}>
              Select 13 cards and click “Find Best Hand”.
            </div>
          )}

          {result && (
            <>
              <PilesView best={result.best} />

              <div style={{ marginTop: 12 }}>
                <div>
                  <strong>Estimated winrate:</strong>{" "}
                  {result.estimated_winrate.toFixed(3)}
                </div>
                <div>
                  <strong>Estimated margin:</strong>{" "}
                  {result.estimated_margin.toFixed(2)}
                </div>
                <div>
                  <strong>Time used:</strong> {result.elapsed_sec.toFixed(2)}s
                </div>
                <div>
                  <strong>Shortlist K:</strong> {result.shortlist_k}
                </div>
              </div>

              <div style={{ marginTop: 10, fontSize: 12, color: "#6b7280" }}>
                Winrate is estimated by Monte Carlo vs 3 heuristic opponents
                under a 3-minute cap.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
