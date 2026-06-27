import { describe, test, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import ApiStatusBadge from "../components/ApiStatusBadge";
import { checkHealth } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  checkHealth: vi.fn(),
}));

const mockCheckHealth = vi.mocked(checkHealth);

describe("ApiStatusBadge", () => {
  beforeEach(() => {
    mockCheckHealth.mockReset();
  });

  test("shows Checking API… before the first health check resolves", () => {
    mockCheckHealth.mockReturnValue(new Promise(() => {})); // never resolves
    render(<ApiStatusBadge />);
    expect(screen.getByText("Checking API…")).toBeTruthy();
  });

  test("shows API connected once the health check returns true", async () => {
    mockCheckHealth.mockResolvedValue(true);
    render(<ApiStatusBadge />);
    await waitFor(() => {
      expect(screen.getByText("API connected")).toBeTruthy();
    });
  });

  test("shows Backend waking up… when the first health check returns false", async () => {
    mockCheckHealth.mockResolvedValue(false);
    render(<ApiStatusBadge />);
    await waitFor(() => {
      expect(screen.getByText("Backend waking up…")).toBeTruthy();
    });
  });
});
