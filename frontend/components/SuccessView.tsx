import AnswerCard from "./AnswerCard";
import SourcesList from "./SourcesList";
import type { AskResponse } from "@/lib/types";

type SuccessViewProps = {
  result: AskResponse;
};

export default function SuccessView({ result }: SuccessViewProps) {
  const hasSources = result.sources.length > 0;

  return (
    <div
      className={
        hasSources
          ? "grid grid-cols-1 items-start gap-6 lg:grid-cols-[1.2fr_1fr]"
          : "mx-auto w-full max-w-[640px]"
      }
    >
      <AnswerCard answer={result.answer} sources={result.sources} />
      {hasSources && <SourcesList sources={result.sources} />}
    </div>
  );
}
