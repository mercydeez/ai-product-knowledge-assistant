import { AlertTriangleIcon } from "./icons";

type ErrorStateProps = {
  message: string | null;
  onRetry: () => void;
};

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="mx-auto my-[6vh] max-w-[440px] text-center">
      <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-error-soft">
        <AlertTriangleIcon className="text-error" />
      </div>
      <h3 className="mb-2 font-serif text-2xl font-medium">
        Something went wrong
      </h3>
      <p className="mb-[22px] text-[15px] leading-relaxed text-muted">
        {message ||
          "We couldn't reach the retrieval service. Please check your connection and try again."}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="rounded-xl bg-accent px-6 py-3 text-sm font-medium text-cream transition-colors hover:bg-accent-strong"
      >
        Try again
      </button>
    </div>
  );
}
