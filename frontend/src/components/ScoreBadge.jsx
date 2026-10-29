const GRADE_COLORS = {
  A: "#1a7f37",
  B: "#4a8f00",
  C: "#b08900",
  D: "#c05600",
  F: "#c0292e",
};

export default function ScoreBadge({ score, grade }) {
  return (
    <div className="score-badge" style={{ borderColor: GRADE_COLORS[grade] || "#888" }}>
      <span className="score-grade" style={{ color: GRADE_COLORS[grade] || "#888" }}>
        {grade}
      </span>
      <span className="score-number">{score}/100</span>
    </div>
  );
}
