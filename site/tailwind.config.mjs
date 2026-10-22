/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"SF Pro Display"',
          '"SF Pro Text"',
          '"Segoe UI"',
          'Roboto',
          'Inter',
          'sans-serif',
        ],
        mono: [
          '"SF Mono"',
          'Menlo',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      },
      colors: {
        titanium: {
          950: '#060608',
          900: '#0b0b10',
          850: '#111118',
          800: '#181822',
          700: '#242432',
          600: '#343446',
        },
        champagne: {
          50: '#fffbf0',
          100: '#fef5d6',
          200: '#fde9aa',
          300: '#fbd773',
          400: '#f7be38',
          500: '#e5a519',
          600: '#c5810e',
          700: '#9d5e0e',
          800: '#804a13',
          900: '#6c3d14',
        },
        gold: {
          light: '#ffdf9e',
          pure: '#e6b96e',
          bronze: '#b38238',
          dark: '#735017',
        }
      },
      boxShadow: {
        'glow-gold': '0 0 35px -5px rgba(230, 185, 110, 0.28)',
        'glow-amber': '0 0 45px -8px rgba(247, 190, 56, 0.22)',
        'glass-titanium': '0 8px 32px 0 rgba(0, 0, 0, 0.55)',
        'inner-gold': 'inset 0 1px 0 0 rgba(255, 223, 158, 0.18)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
