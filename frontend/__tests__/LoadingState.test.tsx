import { describe, test, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import LoadingState from "../components/LoadingState";

describe("LoadingState", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  test("does not show the slow-start hint immediately", () => {
    render(<LoadingState step={0} />);
    expect(screen.queryByText(/Taking longer than usual/)).toBeNull();
  });

  test("shows the slow-start hint after 8 seconds", () => {
    render(<LoadingState step={0} />);
    act(() => {
      vi.advanceTimersByTime(8_000);
    });
    expect(screen.getByText(/Taking longer than usual/)).toBeTruthy();
  });

  test("does not show the hint at 7999ms", () => {
    render(<LoadingState step={0} />);
    act(() => {
      vi.advanceTimersByTime(7_999);
    });
    expect(screen.queryByText(/Taking longer than usual/)).toBeNull();
  });
});
