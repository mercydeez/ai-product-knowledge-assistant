import ApiStatusBadge from "./ApiStatusBadge";

export default function Header() {
  return (
    <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-line bg-cream/85 px-6 py-4 backdrop-blur-md md:px-8">
      <div className="flex items-center gap-3">
        <div className="flex h-[34px] w-[34px] items-center justify-center rounded-[9px] bg-accent font-serif text-xl text-cream shadow-[0_2px_8px_rgba(31,107,79,0.28)]">
          P
        </div>
        <div className="flex flex-col leading-tight">
          <span className="text-[15px] font-semibold tracking-tight">
            Product Knowledge Assistant
          </span>
          <span className="text-[11px] uppercase tracking-wider text-muted-2">
            Retrieval-Augmented Search
          </span>
        </div>
      </div>
      <ApiStatusBadge />
    </header>
  );
}
