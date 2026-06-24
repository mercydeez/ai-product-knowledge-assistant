import SearchBar from "./SearchBar";

type QueryBarProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onReset: () => void;
};

export default function QueryBar({
  value,
  onChange,
  onSubmit,
  onReset,
}: QueryBarProps) {
  return (
    <div className="mb-7 flex items-center gap-3">
      <div className="flex-1">
        <SearchBar
          value={value}
          onChange={onChange}
          onSubmit={onSubmit}
          placeholder="Ask another question…"
          size="compact"
        />
      </div>
      <button
        type="button"
        onClick={onReset}
        className="flex-none whitespace-nowrap rounded-xl border border-line px-4 py-[11px] text-[13.5px] text-muted transition-colors hover:border-muted-3 hover:text-ink"
      >
        Ask another
      </button>
    </div>
  );
}
