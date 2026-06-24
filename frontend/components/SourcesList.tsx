import SourceCard from "./SourceCard";
import type { Source } from "@/lib/types";

type SourcesListProps = {
  sources: Source[];
};

export default function SourcesList({ sources }: SourcesListProps) {
  return (
    <div>
      <div className="mb-4">
        <h2 className="mb-0.5 font-serif text-[22px] font-medium">
          Retrieved Sources
        </h2>
        <p className="text-[13px] text-muted-2">
          The product data used to generate this answer.
        </p>
      </div>
      <div className="flex flex-col gap-3.5">
        {sources.map((source) => (
          <SourceCard key={source.chunk_id} source={source} />
        ))}
      </div>
    </div>
  );
}
