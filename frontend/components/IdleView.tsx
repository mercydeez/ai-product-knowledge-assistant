"use client";

import SearchBar from "./SearchBar";
import { EXAMPLE_QUESTIONS, HOW_IT_WORKS } from "@/lib/examples";

type IdleViewProps = {
  draft: string;
  onDraftChange: (value: string) => void;
  onSubmit: (text?: string) => void;
  inputError: boolean;
};

export default function IdleView({
  draft,
  onDraftChange,
  onSubmit,
  inputError,
}: IdleViewProps) {
  return (
    <section className="mt-[7vh] w-full max-w-[720px] text-center">
      <div className="mb-5 text-xs font-semibold uppercase tracking-[0.16em] text-accent">
        Grounded Product Search
      </div>
      <h1 className="mb-[18px] font-serif text-[44px] font-medium leading-[1.05] tracking-tight text-balance md:text-[52px]">
        Ask anything about the catalog.
      </h1>
      <p className="mx-auto mb-9 max-w-[540px] text-[17px] leading-relaxed text-muted text-pretty">
        Every answer is grounded in real product data — and shows you the
        exact sources it retrieved to get there.
      </p>

      <SearchBar
        value={draft}
        onChange={onDraftChange}
        onSubmit={() => onSubmit()}
        placeholder="I need a breathable cotton shirt for everyday use…"
        size="large"
        autoFocus
      />

      {inputError && (
        <div className="mt-2.5 pl-1 text-left text-[13px] text-error">
          Type a question to search the catalog.
        </div>
      )}

      <div className="mt-[22px] flex flex-wrap justify-center gap-2.5">
        {EXAMPLE_QUESTIONS.map((example) => (
          <button
            key={example.label}
            type="button"
            onClick={() => onSubmit(example.query)}
            className="whitespace-nowrap rounded-full border border-line bg-card px-4 py-2 text-[13.5px] text-ink/80 transition-colors hover:border-accent hover:text-accent-strong"
          >
            {example.label}
          </button>
        ))}
      </div>

      <div className="mt-14 flex justify-center gap-3.5">
        {HOW_IT_WORKS.map((step) => (
          <div
            key={step.num}
            className="max-w-[200px] flex-1 border-t-2 border-line p-4 text-left"
          >
            <div className="mb-1.5 font-serif text-[15px] text-accent">
              {step.num}
            </div>
            <div className="mb-0.5 text-sm font-semibold">{step.title}</div>
            <div className="text-[12.5px] leading-relaxed text-muted-2">
              {step.desc}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
