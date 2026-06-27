"use client";

import { useEffect, useState } from "react";

const STEP_LABELS = [
  "Embedding your question",
  "Searching the vector store",
  "Generating grounded answer",
];

type LoadingStateProps = {
  step: number;
};

export default function LoadingState({ step }: LoadingStateProps) {
  const [showSlowHint, setShowSlowHint] = useState(false);

  useEffect(() => {
    const id = setTimeout(() => setShowSlowHint(true), 8_000);
    return () => clearTimeout(id);
  }, []);

  return (
    <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[1.2fr_1fr]">
      <div className="rounded-[20px] border border-line-soft bg-card p-7">
        <div className="flex flex-col gap-[18px]">
          {STEP_LABELS.map((label, i) => {
            const state = i < step ? "done" : i === step ? "active" : "pending";
            return (
              <div key={label} className="flex items-center gap-3">
                <span
                  className={`flex h-6 w-6 flex-none items-center justify-center rounded-full text-xs font-semibold ${
                    state === "done"
                      ? "bg-accent text-cream"
                      : state === "active"
                        ? "animate-pulse-dot border-2 border-accent bg-accent-soft text-accent-strong"
                        : "bg-line-faint text-muted-3"
                  }`}
                >
                  {state === "done" ? "✓" : i + 1}
                </span>
                <span
                  className={`text-[14.5px] ${
                    state === "pending"
                      ? "text-muted-3"
                      : state === "active"
                        ? "font-medium text-ink"
                        : "text-ink"
                  }`}
                >
                  {label}
                </span>
              </div>
            );
          })}
        </div>
        {showSlowHint && (
          <p className="mt-5 text-center text-xs text-muted-2">
            Taking longer than usual — the backend may be waking from sleep (~30 s)
          </p>
        )}
        <div className="my-[26px] h-px bg-line-soft" />
        <div className="skeleton-line mb-3 h-[13px] w-[92%] rounded-md" />
        <div className="skeleton-line mb-3 h-[13px] w-full rounded-md" />
        <div className="skeleton-line h-[13px] w-[78%] rounded-md" />
      </div>
      <div className="flex flex-col gap-3.5">
        <div className="skeleton-line h-[86px] rounded-2xl" />
        <div className="skeleton-line h-[86px] rounded-2xl" />
        <div className="skeleton-line h-[86px] rounded-2xl" />
      </div>
    </div>
  );
}
