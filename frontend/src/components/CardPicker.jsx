import React, { useMemo } from "react";

const RANKS = "23456789TJQKA".split("");
const SUITS = ["C", "D", "H", "S"]; // columns

function suitSymbol(s) {
  if (s === "H") return "♥";
  if (s === "D") return "♦";
  if (s === "S") return "♠";
  return "♣";
}

function suitClass(s) {
  return s === "H" || s === "D" ? "suit-red" : "suit-black";
}

function chunk2(arr) {
  const out = [];
  for (let i = 0; i < arr.length; i += 2) out.push(arr.slice(i, i + 2));
  return out;
}

export default function CardPicker({ selected, onToggle }) {
  // 13 ranks => 6 rows of 2 + last row of 1
  const rankPairs = useMemo(() => chunk2(RANKS), []);

  return (
    <div className="pair-grid">
      {rankPairs.map((pair, idx) => (
        <div className="pair-row" key={idx}>
          {pair.map((r) => (
            <div className="rank-block" key={r}>
              <div className="rank-label">{r}</div>

              <div className="rank-row-cards">
                {SUITS.map((s) => {
                  const code = `${r}${s}`;
                  const isSel = selected.includes(code);

                  return (
                    <button
                      key={code}
                      type="button"
                      className={`card card-tile ${isSel ? "selected" : ""}`}
                      onClick={() => onToggle(code)}
                      title={code}
                      aria-pressed={isSel}
                    >
                      <div className="card-rank">{r}</div>
                      <div className={`card-suit ${suitClass(s)}`}>
                        {suitSymbol(s)}
                      </div>
                      <div className="card-meta">{s}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
