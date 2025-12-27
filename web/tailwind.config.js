/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(220 13% 91%)",
        input: "hsl(220 13% 91%)",
        ring: "hsl(210 24% 60%)",
        background: "hsl(210 17% 98%)",
        foreground: "hsl(210 24% 20%)",
        primary: {
          DEFAULT: "hsl(210 24% 60%)",
          foreground: "hsl(0 0% 100%)",
        },
        secondary: {
          DEFAULT: "hsl(210 16% 93%)",
          foreground: "hsl(210 24% 30%)",
        },
        muted: {
          DEFAULT: "hsl(210 16% 96%)",
          foreground: "hsl(210 12% 50%)",
        },
        card: {
          DEFAULT: "hsl(0 0% 100%)",
          foreground: "hsl(210 24% 20%)",
        },
        accent: {
          DEFAULT: "hsl(210 24% 60%)",
          foreground: "hsl(0 0% 100%)",
        },
      },
      fontFamily: {
        mono: ['IBM Plex Mono', 'Menlo', 'Monaco', 'monospace'],
        serif: ['Crimson Pro', 'Georgia', 'serif'],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}
