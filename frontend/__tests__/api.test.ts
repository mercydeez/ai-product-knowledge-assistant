import { describe, test, expect, vi, beforeEach, afterEach } from "vitest";
import { askQuestionStream, checkHealth, ApiError } from "../lib/api";

function makeStream(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk));
      }
      controller.close();
    },
  });
}

function sse(payload: object): string {
  return `data: ${JSON.stringify(payload)}\n\n`;
}

describe("askQuestionStream", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function mockStream(chunks: string[]) {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      body: makeStream(chunks),
    } as unknown as Response);
  }

  test("calls onSources with parsed sources from the first event", async () => {
    const sources = [{ product_id: "SKU-1001", text: "cotton shirt", score: 0.9 }];
    mockStream([sse({ type: "sources", sources })]);

    const onSources = vi.fn();
    await askQuestionStream("q", { onSources });
    expect(onSources).toHaveBeenCalledWith(sources);
  });

  test("calls onToken once per token event, in order", async () => {
    mockStream([
      sse({ type: "sources", sources: [] }),
      sse({ type: "token", text: "Hello" }),
      sse({ type: "token", text: " world" }),
      sse({ type: "done" }),
    ]);

    const onToken = vi.fn();
    await askQuestionStream("q", { onToken });
    expect(onToken).toHaveBeenCalledTimes(2);
    expect(onToken).toHaveBeenNthCalledWith(1, "Hello");
    expect(onToken).toHaveBeenNthCalledWith(2, " world");
  });

  test("calls onDone when the stream signals completion", async () => {
    mockStream([sse({ type: "sources", sources: [] }), sse({ type: "done" })]);

    const onDone = vi.fn();
    await askQuestionStream("q", { onDone });
    expect(onDone).toHaveBeenCalledOnce();
  });

  test("throws ApiError carrying the server message on an error event", async () => {
    mockStream([sse({ type: "error", message: "Something went wrong" })]);

    const error = await askQuestionStream("q", {}).catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.message).toBe("Something went wrong");
  });

  test("throws ApiError when the HTTP response is not ok", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: "Rate limit exceeded" }),
    } as unknown as Response);

    const error = await askQuestionStream("q", {}).catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.message).toBe("Rate limit exceeded");
  });

  test("parses an event correctly when it arrives split across two network chunks", async () => {
    const full = sse({ type: "token", text: "split" });
    const mid = Math.floor(full.length / 2);
    mockStream([full.slice(0, mid), full.slice(mid)]);

    const onToken = vi.fn();
    await askQuestionStream("q", { onToken });
    expect(onToken).toHaveBeenCalledWith("split");
  });
});

describe("checkHealth", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("returns true when the API responds with ok", async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: true } as Response);
    expect(await checkHealth()).toBe(true);
  });

  test("returns false when the API responds with a non-ok status", async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: false } as Response);
    expect(await checkHealth()).toBe(false);
  });

  test("returns false on a network error", async () => {
    vi.mocked(fetch).mockRejectedValue(new Error("Network error"));
    expect(await checkHealth()).toBe(false);
  });
});
