# Frontend — AI Product Knowledge Assistant

Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS v4 UI for the [AI Product Knowledge Assistant](../README.md). Calls the FastAPI backend's `/ask` and `/ask/stream` endpoints and renders the grounded answer alongside its ranked, retrieved sources.

See the root [`README.md`](../README.md) for setup, the live demo link, and deployment instructions; see [`../design.md`](../design.md) for the full architecture and API contract.

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — the backend (see root README) must be running first.
