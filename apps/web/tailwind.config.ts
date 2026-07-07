import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#f5f7fb",
        ink: "#0f172a",
        accent: "#f97316",
        accentSoft: "#ffedd5",
        line: "#d9e2f1",
        hub: {
          black: "#090909",
          bg: "#121212",
          panel: "#1b1b1b",
          muted: "#a3a3a3",
          text: "#fafafa",
          orange: "#f97316",
          border: "rgba(255,255,255,0.10)",
        },
      },
      boxShadow: {
        card: "0 18px 40px rgba(0, 0, 0, 0.24)",
      },
    },
  },
  plugins: [],
};

export default config;
