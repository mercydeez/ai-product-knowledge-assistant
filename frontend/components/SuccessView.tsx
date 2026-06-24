import AnswerCard from "./AnswerCard";
import SourcesList from "./SourcesList";
import type { AskResponse } from "@/lib/types";

type SuccessViewProps = {
  result: AskResponse;
};

export default function SuccessView({ result }: SuccessViewProps) {
  return (
    <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[1.2fr_1fr]">
      <AnswerCard answer={result.answer} sources={result.sources} />
      <SourcesList sources={result.sources} />
    </div>
  );
}
