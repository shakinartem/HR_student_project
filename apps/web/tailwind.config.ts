import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Dark premium theme
        bg: {
          primary: "#0F0F0F",
          secondary: "#1A1A1A",
          card: "#1F1F1F",
        },
        text: {
          primary: "#FFFFFF",
          secondary: "#A8A8A8",
        },
        accent: {
          DEFAULT: "#F9A602",
          hover: "#FFB733",
        },
        border: "rgba(255,255,255,0.08)",
        // Legacy aliases for compatibility
        surface: "#1F1F1F",
        ink: "#FFFFFF",
        accentSoft: "#2A2A2A",
        line: "rgba(255,255,255,0.08)",
        hub: {
          black: "#0F0F0F",
          bg: "#1A1A1A",
          panel: "#1F1F1F",
          muted: "#A8A8A8",
          text: "#FFFFFF",
          orange: "#F9A602",
          border: "rgba(255,255,255,0.08)",
        },
      },
      boxShadow: {
        card: "0 18px 40px rgba(0, 0, 0, 0.40)",
        button: "0 4px 12px rgba(249, 166, 2, 0.25)",
        buttonHover: "0 6px 16px rgba(249, 166, 2, 0.35)",
      },
      borderRadius: {
        xl: "18px",
      },
    },
  },
  plugins: [],
};

export default config;
