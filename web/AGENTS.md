# AGENTS.md

## Project Overview

A minimalist, geek-style documentation and demonstration site for LSAP (Language Server Agent Protocol).

## Tech Stack

- Runtime: Bun
- Framework: React 19 + Vite
- Styling: Tailwind CSS v3 + shadcn/ui (custom)
- Routing: React Router v7
- Content: React Markdown + remark-gfm
- Icons: Lucide React

## Project Structure

- `src/components/ui/`: Custom shadcn/ui components.
- `src/pages/`: Main application views (`HomePage`, `DocsPage`).
- `src/styles/`: Global styles and Tailwind configuration.
- `public/docs/`: Markdown documentation (source from `@docs/`).

## Quick Start

```bash
cd web
bun install
bun run dev      # http://localhost:3000
bun run build    # Output to dist/
```

## Design System

- Fonts: `IBM Plex Mono` (Technical elements), `Crimson Pro` (Body text).
- Colors: Background `hsl(210 17% 98%)`, Primary `hsl(210 24% 60%)`.
- Aesthetic: Minimalist, low saturation, high legibility, and subtle micro-interactions.

## Key Features

1. Interactive Showcase: Visualizes the 4-step pipeline: Intent → Request → Processing → Result.
2. Docs Engine: Markdown-based documentation system with code highlighting and GFM support.

## Development Notes

- Use `.cjs` for PostCSS config to ensure ESM compatibility.
- Ensure documentation files are synced from the root `@docs/` directory to `public/docs/`.
- Use `Chrome DevTools` MCP for debugging and visual adjustments.
