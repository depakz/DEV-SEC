import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ScoreBadge from "../ScoreBadge.jsx";

describe("ScoreBadge", () => {
  it("renders the grade and score", () => {
    render(<ScoreBadge score={92} grade="A" />);
    expect(screen.getByText("A")).toBeInTheDocument();
    expect(screen.getByText("92/100")).toBeInTheDocument();
  });
});
