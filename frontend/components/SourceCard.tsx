import { CATEGORY_ICONS } from "./icons";
import { colorToHex, luminance } from "@/lib/chunk";
import type { Source } from "@/lib/types";

type SourceCardProps = {
  source: Source;
};

export default function SourceCard({ source }: SourceCardProps) {
  const category = source.category || "Product";
  const swatchHex = colorToHex(source.color || null);
  const swatchFg = luminance(swatchHex) > 0.62 ? "#1b1a17" : "#f6f4ef";
  const swatchBorder =
    luminance(swatchHex) > 0.78 ? "1px solid rgba(0,0,0,0.10)" : "none";
  const pct = Math.round(Math.max(0, Math.min(1, source.score)) * 100);
  const CategoryIcon = CATEGORY_ICONS[source.category];

  return (
    <div className="rounded-2xl border border-line-soft bg-card p-[18px]">
      <div className="flex items-start gap-3.5">
        <div
          className="flex h-[54px] w-[54px] flex-none items-center justify-center rounded-[13px] font-serif text-2xl font-medium"
          style={{
            backgroundColor: swatchHex,
            color: swatchFg,
            border: swatchBorder,
          }}
        >
          {CategoryIcon ? (
            <CategoryIcon className="h-7 w-7" />
          ) : (
            source.product_name.charAt(0)
          )}
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-0.5 flex items-center gap-2">
            <span className="font-serif text-[15px] font-semibold text-accent">
              #{source.rank}
            </span>
            <span className="truncate text-[15px] font-semibold tracking-tight">
              {source.product_name}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-2">
            <span className="font-mono tracking-wide">
              {source.product_id}
            </span>
            <span className="h-[3px] w-[3px] rounded-full bg-muted-3" />
            <span className="uppercase tracking-wide">{category}</span>
          </div>
        </div>
        <div className="flex-none text-right">
          <div className="font-serif text-[19px] font-semibold leading-none text-ink">
            {pct}%
          </div>
          <div className="mt-0.5 text-[10px] uppercase tracking-wide text-muted-3">
            match
          </div>
        </div>
      </div>

      <div className="my-3.5 h-[5px] overflow-hidden rounded-full bg-line-faint">
        <div
          className="h-full rounded-full bg-accent transition-[width] duration-700 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="max-h-[132px] overflow-y-auto whitespace-pre-wrap rounded-[10px] border border-line-faint bg-card-soft px-3.5 py-3 font-mono text-[11.5px] leading-relaxed text-muted">
        {source.text}
      </div>
    </div>
  );
}
