"use client";

import { useEffect, useRef, useState } from "react";
import Header from "@/components/Header";
import IdleView from "@/components/IdleView";
import QueryBar from "@/components/QueryBar";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import SuccessView from "@/components/SuccessView";
import { askQuestion, ApiError } from "@/lib/api";
import type { AskResponse } from "@/lib/types";

type Status = "idle" | "loading" | "error" | "success";

export default function Home() {
  const [draft, setDraft] = useState("");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [inputError, setInputError] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  function clearTimers() {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
  }

  useEffect(() => clearTimers, []);

  function submit(text?: string) {
    const question = (text ?? draft).trim();
    if (!question) {
      setInputError(true);
      return;
    }

    clearTimers();
    setStatus("loading");
    setDraft(question);
    setQuery(question);
    setLoadingStep(0);
    setInputError(false);
    setResult(null);
    setErrorMessage(null);

    timersRef.current.push(setTimeout(() => setLoadingStep(1), 500));
    timersRef.current.push(setTimeout(() => setLoadingStep(2), 1000));

    askQuestion(question)
      .then((response) => {
        setResult(response);
        setStatus("success");
      })
      .catch((error: unknown) => {
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
    setStatus("idle");
    setDraft("");
    setQuery("");
    setLoadingStep(0);
    setResult(null);
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
            {status === "success" && result && <SuccessView result={result} />}
          </section>
        )}
      </main>
    </>
  );
}
