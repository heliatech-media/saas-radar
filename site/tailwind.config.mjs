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
          950: '#030303',
          900: '#070b12',
          850: '#0c121e',
          800: '#111927',
          700: '#1e293b',
          600: '#334155',
        },
        neon: {
          cyan: '#06b6d4',
          'cyan-bright': '#22d3ee',
          'cyan-sky': '#38bdf8',
          fuchsia: '#d946ef',
          'fuchsia-bright': '#f472b6',
          violet: '#a855f7',
        }
      },
      boxShadow: {
        'glow-cyan': '0 0 35px -5px rgba(6, 182, 212, 0.35)',
        'glow-fuchsia': '0 0 35px -5px rgba(217, 70, 239, 0.35)',
        'glow-cyber': '0 0 45px -8px rgba(6, 182, 212, 0.25), 0 0 45px -8px rgba(217, 70, 239, 0.20)',
        'glass-cyber': '0 8px 32px 0 rgba(0, 0, 0, 0.7)',
        'inner-cyan': 'inset 0 1px 0 0 rgba(34, 211, 238, 0.25)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [typography],
}
