/** @type {import('tailwindcss').Config} */
import typography from '@tailwindcss/typography';

export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif',
        ],
        display: [
          '"Space Grotesk"',
          'Inter',
          'sans-serif',
        ],
        mono: [
          '"JetBrains Mono"',
          '"SF Mono"',
          'Menlo',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      },
      colors: {
        cyber: {
          950: '#030508',
          900: '#05070B',
          850: '#080C14',
          800: '#0B101B',
          700: '#111726',
          600: '#182033',
        },
        obsidian: {
          950: '#030508',
          900: '#05070B',
          850: '#080C14',
          800: '#0B101B',
          700: '#111726',
          600: '#182033',
        },
        cobalt: {
          400: '#38BDF8',
          500: '#0EA5E9',
          600: '#0284C7',
          700: '#0369A1',
        },
        neon: {
          cyan: '#38bdf8',
          'cyan-bright': '#38bdf8',
          'cyan-sky': '#38bdf8',
          fuchsia: '#0284c7',
          'fuchsia-bright': '#38bdf8',
          violet: '#6366f1',
        },
        hairline: 'rgba(255, 255, 255, 0.08)',
        'hairline-hover': 'rgba(255, 255, 255, 0.16)',
        'hairline-cobalt': 'rgba(2, 132, 199, 0.35)',
      },
      boxShadow: {
        'glow-cyan': '0 0 25px -5px rgba(2, 132, 199, 0.25)',
        'glow-fuchsia': '0 0 25px -5px rgba(56, 189, 248, 0.20)',
        'glow-cyber': '0 0 35px -8px rgba(2, 132, 199, 0.20)',
        'glass-cyber': '0 8px 32px 0 rgba(0, 0, 0, 0.8)',
        'inner-cyan': 'inset 0 1px 0 0 rgba(56, 189, 248, 0.20)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [typography],
}
