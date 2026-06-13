export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? "http://192.168.0.39:8000";

export const C = {
  bg:           "#010414",
  surface800:   "#081727",
  surface700:   "#0F2338",
  surface600:   "#172E4A",
  brand600:     "#0361E3",
  brand500:     "#0E86FD",
  brand400:     "#1EB2FF",
  brand300:     "#41E2FF",
  textPrimary:  "#d9eaf8",
  textSecondary:"#8BA7BC",
  textMuted:    "#4E6478",
  border:       "#0F2338",
  success:      "#22c55e",
  error:        "#ef4444",
  amber:        "#f59e0b",
  purple:       "#a78bfa",
} as const;
