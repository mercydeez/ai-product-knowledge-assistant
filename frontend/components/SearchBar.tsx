"use client";

import { ArrowRightIcon } from "./icons";

type SearchBarProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  placeholder: string;
  size?: "large" | "compact";
  autoFocus?: boolean;
};

export default function SearchBar({
  value,
  onChange,
  onSubmit,
  placeholder,
  size = "large",
  autoFocus,
}: SearchBarProps) {
  const isLarge = size === "large";

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      onSubmit();
    }
  }

  return (
    <div
      className={`flex w-full items-center gap-2.5 rounded-2xl border border-line bg-card ${
        isLarge
          ? "p-2 pl-5 shadow-[0_8px_30px_-12px_rgba(27,26,23,0.18)]"
          : "rounded-[14px] p-1.5 pl-4"
      }`}
    >
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className={`flex-1 bg-transparent text-ink outline-none ${
          isLarge ? "py-2.5 text-base" : "py-2 text-[15px]"
        }`}
      />
      <button
        type="button"
        onClick={onSubmit}
        aria-label="Send"
        className={`flex flex-none items-center justify-center rounded-xl bg-accent text-cream transition-all hover:-translate-y-px hover:bg-accent-strong ${
          isLarge ? "h-[46px] w-[46px]" : "h-[38px] w-[38px] rounded-[10px]"
        }`}
      >
        <ArrowRightIcon className={isLarge ? "" : "h-[18px] w-[18px]"} />
      </button>
    </div>
  );
}
