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
        serif: ['Georgia', 'Times New Roman', 'serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: '#b45309', // amber-700
          light: '#d97706', // amber-600
          dark: '#92400e', // amber-800
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: '#57534e', // stone-600
          light: '#78716c', // stone-500
          dark: '#44403c', // stone-700
          foreground: 'hsl(var(--secondary-foreground))',
        },
        accent: {
          DEFAULT: '#f59e0b', // amber-500
          foreground: 'hsl(var(--accent-foreground))',
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
          from: { opacity: 0, transform: 'translateY(10px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-up': 'slide-up 0.4s ease-out',
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#44403c',
            a: {
              color: '#b45309',
              '&:hover': {
                color: '#92400e',
              },
            },
            h1: {
              fontFamily: 'Georgia, Times New Roman, serif',
              color: '#292524',
            },
            h2: {
              fontFamily: 'Georgia, Times New Roman, serif',
              color: '#292524',
            },
            h3: {
              fontFamily: 'Georgia, Times New Roman, serif',
              color: '#292524',
            },
          },
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
