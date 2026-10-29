import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import DomainForm from "../DomainForm.jsx";

describe("DomainForm", () => {
  it("does not submit an empty domain", () => {
    const onSubmit = vi.fn();
    render(<DomainForm onSubmit={onSubmit} loading={false} />);
    fireEvent.click(screen.getByRole("button"));
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits the trimmed domain typed in", () => {
    const onSubmit = vi.fn();
    render(<DomainForm onSubmit={onSubmit} loading={false} />);
    fireEvent.change(screen.getByLabelText("Domain to scan"), {
      target: { value: "  example.com  " },
    });
    fireEvent.click(screen.getByRole("button"));
    expect(onSubmit).toHaveBeenCalledWith("example.com");
  });

  it("disables the button while loading", () => {
    render(<DomainForm onSubmit={vi.fn()} loading={true} />);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
