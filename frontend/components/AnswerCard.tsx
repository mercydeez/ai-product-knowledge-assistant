import { AlertTriangleIcon, CheckIcon } from "./icons";
import type { Source } from "@/lib/types";

type AnswerCardProps = {
  answer: string;
  sources: Source[];
  isStreaming?: boolean;
};

export default function AnswerCard({ answer, sources, isStreaming = false }: AnswerCardProps) {
  const paragraphs = answer
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);

  const seen = new Set<string>();
  const chips = sources.filter((source) => {
    if (seen.has(source.product_id)) return false;
    seen.add(source.product_id);
    return true;
  });

  return (
    <div className="rounded-[20px] border border-line-soft bg-card p-7 shadow-[0_12px_40px_-20px_rgba(27,26,23,0.2)] md:p-8">
      <div className="mb-[18px] flex items-center justify-between gap-3">
        <span className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-2">
          Answer
        </span>
        {sources.length > 0 ? (
          <span className="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full bg-accent-soft px-[11px] py-[5px] text-xs font-semibold text-accent-strong">
            <CheckIcon />
            Grounded in {sources.length} sources
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full bg-line-faint px-[11px] py-[5px] text-xs font-semibold text-muted">
            <AlertTriangleIcon className="h-3 w-3" />
            Outside catalog scope
          </span>
        )}
      </div>

      <div className="text-[17.5px] leading-relaxed text-ink/90">
        {paragraphs.length === 0 && isStreaming && (
          <p className="mb-3.5 text-pretty">
            <span className="inline-block h-4 w-[2px] animate-pulse bg-ink/60 align-middle" />
          </p>
        )}
        {paragraphs.map((para, i) => (
          <p key={i} className="mb-3.5 text-pretty">
            {para}
            {isStreaming && i === paragraphs.length - 1 && (
              <span className="ml-1 inline-block h-4 w-[2px] animate-pulse bg-ink/60 align-middle" />
            )}
          </p>
        ))}
      </div>

      {chips.length > 0 && (
        <>
          <div className="my-[18px] h-px bg-line-faint" />
          <div className="flex flex-wrap items-center gap-2">
            <span className="mr-1 text-[12.5px] text-muted-2">Sources:</span>
            {chips.map((source) => (
              <span
                key={source.product_id}
                className="inline-flex items-center gap-1.5 rounded-full border border-line-soft bg-cream px-[11px] py-[5px] text-[12.5px] text-ink/80"
              >
                <span className="font-serif font-semibold text-accent">
                  #{source.rank}
                </span>
                {source.product_name}
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
