"use client";

import { useEffect, useRef, useState } from "react";
import Header from "@/components/Header";
import IdleView from "@/components/IdleView";
import QueryBar from "@/components/QueryBar";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import SuccessView from "@/components/SuccessView";
import { askQuestionStream, ApiError } from "@/lib/api";
import type { AskResponse } from "@/lib/types";

type Status = "idle" | "loading" | "error" | "success";

export default function Home() {
  const [draft, setDraft] = useState("");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [inputError, setInputError] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  const revealQueueRef = useRef("");
  const revealTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const streamDoneRef = useRef(false);

  function clearTimers() {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
  }

  function stopReveal() {
    if (revealTimerRef.current) {
      clearInterval(revealTimerRef.current);
      revealTimerRef.current = null;
    }
  }

  // Groq's inference is fast enough that a whole short answer can arrive
  // within ~150ms of the first token, too quick to perceive as "typing." This
  // paces the reveal on the client so the genuinely-streamed text is still
  // visible token-by-token, independent of how bursty the real network
  // delivery is.
  function startReveal() {
    if (revealTimerRef.current) return;
    revealTimerRef.current = setInterval(() => {
      if (revealQueueRef.current.length > 0) {
        const chunk = revealQueueRef.current.slice(0, 2);
        revealQueueRef.current = revealQueueRef.current.slice(2);
        setResult((prev) => (prev ? { ...prev, answer: prev.answer + chunk } : prev));
      } else if (streamDoneRef.current) {
        stopReveal();
        setIsStreaming(false);
      }
    }, 18);
  }

  useEffect(() => {
    return () => {
      clearTimers();
      stopReveal();
      abortRef.current?.abort();
    };
  }, []);

  function submit(text?: string) {
    const question = (text ?? draft).trim();
    if (!question) {
      setInputError(true);
      return;
    }

    clearTimers();
    stopReveal();
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    revealQueueRef.current = "";
    streamDoneRef.current = false;

    setStatus("loading");
    setDraft(question);
    setQuery(question);
    setLoadingStep(0);
    setInputError(false);
    setResult(null);
    setIsStreaming(false);
    setErrorMessage(null);

    timersRef.current.push(setTimeout(() => setLoadingStep(1), 500));
    timersRef.current.push(setTimeout(() => setLoadingStep(2), 1000));

    askQuestionStream(
      question,
      {
        onSources: (sources) => {
          setResult({ question, answer: "", sources });
          setIsStreaming(true);
          setStatus("success");
          startReveal();
        },
        onToken: (text) => {
          revealQueueRef.current += text;
        },
        onDone: () => {
          streamDoneRef.current = true;
        },
      },
      controller.signal,
    ).catch((error: unknown) => {
      if (controller.signal.aborted) return;
      stopReveal();
      setIsStreaming(false);
      setErrorMessage(
        error instanceof ApiError || error instanceof Error
          ? error.message
          : null,
      );
      setStatus("error");
    });
  }

  function handleReset() {
    clearTimers();
    stopReveal();
    abortRef.current?.abort();
    setStatus("idle");
    setDraft("");
    setQuery("");
    setLoadingStep(0);
    setResult(null);
    setIsStreaming(false);
    setInputError(false);
    setErrorMessage(null);
  }

  return (
    <>
      <Header />
      <main className="flex flex-1 flex-col items-center px-6 py-8 md:px-8">
        {status === "idle" ? (
          <IdleView
            draft={draft}
            onDraftChange={(value) => {
              setDraft(value);
              setInputError(false);
            }}
            onSubmit={submit}
            inputError={inputError}
          />
        ) : (
          <section className="w-full max-w-[1080px]">
            <QueryBar
              value={draft}
              onChange={setDraft}
              onSubmit={() => submit()}
              onReset={handleReset}
            />
            {status === "loading" && <LoadingState step={loadingStep} />}
            {status === "error" && (
              <ErrorState message={errorMessage} onRetry={() => submit(query)} />
            )}
            {status === "success" && result && (
              <SuccessView result={result} isStreaming={isStreaming} />
            )}
          </section>
        )}
      </main>
    </>
  );
}
