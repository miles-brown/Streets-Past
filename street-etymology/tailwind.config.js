/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      fontFamily: {
        display: ['Syne', 'system-ui', 'sans-serif'],
        sans: ['"DM Sans"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
        serif: ['Georgia', 'Times New Roman', 'serif'],
      },
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        urban: {
          50: '#f4f4f5',
          100: '#e4e4e7',
          200: '#d4d4d8',
          300: '#a1a1aa',
          400: '#71717a',
          500: '#52525b',
          600: '#3f3f46',
          700: '#27272a',
          800: '#18181b',
          850: '#12141c',
          900: '#0f1117',
          950: '#090a0e',
        },
        signal: {
          DEFAULT: '#22d3ee',
          dim: '#0891b2',
          glow: '#67e8f9',
        },
        heritage: {
          gold: '#c4a35a',
          brown: '#8b4513',
          parchment: '#f5f1e6',
          ink: '#1a1a1a',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
        '2xl': '1rem',
        '3xl': '1.25rem',
      },
      boxShadow: {
        paper: '0 1px 0 0 hsl(25 22% 88% / 0.9), 0 12px 40px -16px hsl(25 30% 20% / 0.12)',
        'paper-dark':
          '0 1px 0 0 hsl(20 12% 22% / 0.9), 0 20px 50px -20px hsl(0 0% 0% / 0.45)',
      },
      backgroundImage: {
        'grid-fine':
          "linear-gradient(hsl(var(--border) / 0.5) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--border) / 0.5) 1px, transparent 1px)",
        'hero-mesh':
          'radial-gradient(ellipse 85% 55% at 50% -25%, hsl(var(--primary) / 0.12), transparent 55%), radial-gradient(ellipse 45% 35% at 100% 0%, hsl(355 35% 50% / 0.08), transparent 50%)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: 0 },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: 0 },
        },
        'fade-in': {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        'slide-up': {
          from: { opacity: 0, transform: 'translateY(12px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'fade-in': 'fade-in 0.4s ease-out',
        'slide-up': 'slide-up 0.5s ease-out',
      },
      typography: {
        DEFAULT: {
          css: {
            color: 'hsl(var(--muted-foreground))',
            a: {
              color: 'hsl(var(--primary))',
              '&:hover': { opacity: '0.85' },
            },
            h1: { fontFamily: 'Syne, system-ui, sans-serif', color: 'hsl(var(--foreground))' },
            h2: { fontFamily: 'Syne, system-ui, sans-serif', color: 'hsl(var(--foreground))' },
            h3: { fontFamily: 'Syne, system-ui, sans-serif', color: 'hsl(var(--foreground))' },
          },
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
