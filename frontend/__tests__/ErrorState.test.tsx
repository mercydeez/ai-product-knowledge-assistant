import { describe, test, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ErrorState from "../components/ErrorState";

describe("ErrorState", () => {
  test("renders the custom message when one is provided", () => {
    render(<ErrorState message="Custom error text" onRetry={() => {}} />);
    expect(screen.getByText("Custom error text")).toBeTruthy();
  });

  test("renders the default message when message is null", () => {
    render(<ErrorState message={null} onRetry={() => {}} />);
    expect(screen.getByText(/couldn't reach the retrieval service/)).toBeTruthy();
  });

  test("calls onRetry when the retry button is clicked", () => {
    const onRetry = vi.fn();
    render(<ErrorState message={null} onRetry={onRetry} />);
    fireEvent.click(screen.getByRole("button", { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledOnce();
  });
});
