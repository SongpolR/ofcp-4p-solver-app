import React from "react";

function suitSymbol(s) {
  if (s === "H") return "♥";
  if (s === "D") return "♦";
  if (s === "S") return "♠";
  return "♣";
}

function suitClass(s) {
  return s === "H" || s === "D" ? "suit-red" : "suit-black";
}

function ResultCard({ code }) {
  const r = code[0];
  const s = code[1];

  return (
    <div className="card card-mini">
      <div className="card-rank">{r}</div>
      <div className={`card-suit ${suitClass(s)}`}>{suitSymbol(s)}</div>
      <div className="card-meta">{s}</div>
    </div>
  );
}

function Pile({ title, cards, expected }) {
  return (
    <div className="pile">
      <div
        className="row"
        style={{ justifyContent: "space-between", alignItems: "center" }}
      >
        <strong>{title}</strong>
        <span className="badge">
          {cards?.length ?? 0}/{expected}
        </span>
      </div>

      <div className="result-cards">
        {(cards || []).map((c) => (
          <ResultCard key={c} code={c} />
        ))}
      </div>
    </div>
  );
}

export default function PilesView({ best }) {
  if (!best) return null;

  return (
    <div className="piles">
      <Pile title="Top" cards={best.top} expected={3} />
      <Pile title="Middle" cards={best.middle} expected={5} />
      <Pile title="Bottom" cards={best.bottom} expected={5} />
    </div>
  );
}
