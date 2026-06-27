"use client";

import { useEffect, useRef, useState } from "react";
import { checkHealth } from "@/lib/api";

type Status = "checking" | "online" | "waking" | "offline";

const WAKE_TIMEOUT_MS = 90_000;
const POLL_INTERVAL_MS = 5_000;

export default function ApiStatusBadge() {
  const [status, setStatus] = useState<Status>("checking");
  const wakingStartRef = useRef<number | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const online = await checkHealth();
      if (cancelled) return;

      if (online) {
        wakingStartRef.current = null;
        setStatus("online");
      } else if (wakingStartRef.current === null) {
        wakingStartRef.current = Date.now();
        setStatus("waking");
      } else if (Date.now() - wakingStartRef.current > WAKE_TIMEOUT_MS) {
        setStatus("offline");
      }
      // else stays "waking" — keep retrying
    }

    poll();
    const interval = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const dotColor =
    status === "offline"
      ? "bg-error"
      : status === "waking"
        ? "bg-warning"
        : "bg-accent";

  const label =
    status === "checking"
      ? "Checking API…"
      : status === "online"
        ? "API connected"
        : status === "waking"
          ? "Backend waking up…"
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
