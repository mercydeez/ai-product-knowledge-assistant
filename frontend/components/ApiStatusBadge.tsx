"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";

type Status = "checking" | "online" | "offline";

export default function ApiStatusBadge() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const online = await checkHealth();
      if (!cancelled) setStatus(online ? "online" : "offline");
    }

    poll();
    const interval = setInterval(poll, 30_000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const dotColor = status === "offline" ? "bg-error" : "bg-accent";
  const label =
    status === "checking"
      ? "Checking API…"
      : status === "online"
        ? "API connected"
        : "API unreachable";

  return (
    <div className="flex items-center gap-2 rounded-full border border-line bg-card px-3 py-1.5">
      <span
        className={`h-[7px] w-[7px] rounded-full ${dotColor} ${status !== "offline" ? "animate-pulse-dot" : ""}`}
      />
      <span className="whitespace-nowrap text-xs font-medium text-muted">
        {label}
      </span>
    </div>
  );
}
