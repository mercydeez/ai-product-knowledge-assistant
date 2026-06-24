const COLOR_HEX: Record<string, string> = {
  white: "#f1efe9",
  black: "#1b1a17",
  coral: "#e6836b",
  beige: "#d8c6a6",
  navy: "#2a3a57",
  olive: "#6f6c3f",
  lavender: "#c6bce0",
  charcoal: "#3a3a3c",
  emerald: "#1f6b4f",
  "forest green": "#2b432f",
  "heather grey": "#b6b4ad",
  "dusty rose": "#c99aa0",
  mustard: "#c9a227",
  sage: "#8a9b7e",
};

const DEFAULT_SWATCH = "#cfc8bb";

export function colorToHex(color: string | null): string {
  if (!color) return DEFAULT_SWATCH;
  return COLOR_HEX[color.toLowerCase()] ?? DEFAULT_SWATCH;
}

export function luminance(hex: string): number {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16) / 255;
  const g = parseInt(h.slice(2, 4), 16) / 255;
  const b = parseInt(h.slice(4, 6), 16) / 255;
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
