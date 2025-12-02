/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Premium Studio Theme - Refined Dark Palette
        'studio': {
          // Core darks with subtle warmth
          'void': '#08070a',
          'abyss': '#0d0c10',
          'black': '#121117',
          'charcoal': '#1a1820',
          'graphite': '#24222c',
          'slate': '#3d3a47',

          // Warm neutrals
          'stone': '#6b6778',
          'sand': '#a9a4b5',
          'pearl': '#d4d0df',
          'cream': '#f5f3fa',

          // Primary accent - Rose Gold / Champagne
          'rose': {
            50: '#fdf8f6',
            100: '#f9ebe5',
            200: '#f2d5c9',
            300: '#e8b8a5',
            400: '#dc9a7f',
            500: '#cc7a5a',
            600: '#b86347',
            700: '#9a4f3a',
            800: '#7d4133',
            900: '#66372d',
          },

          // Secondary accent - Amber/Gold
          'amber': '#d4a574',
          'gold': '#c9a227',
          'bronze': '#b8860b',
          'copper': '#cd7f32',

          // Tertiary accent - Purple haze
          'violet': {
            50: '#f5f3ff',
            100: '#ede9fe',
            200: '#ddd6fe',
            300: '#c4b5fd',
            400: '#a78bfa',
            500: '#8b5cf6',
            600: '#7c3aed',
            700: '#6d28d9',
            800: '#5b21b6',
            900: '#4c1d95',
          },

          // Status colors - Refined
          'success': '#34d399',
          'success-dim': '#065f46',
          'error': '#f87171',
          'error-dim': '#7f1d1d',
          'warning': '#fbbf24',
          'warning-dim': '#78350f',
          'info': '#60a5fa',
          'info-dim': '#1e3a5f',

          // VU Meter colors
          'vu-green': '#4ade80',
          'vu-yellow': '#facc15',
          'vu-red': '#ef4444',
        },

        // Legacy support
        'sf-bg': {
          DEFAULT: '#08070a',
          secondary: '#0d0c10',
          card: '#121117',
          hover: '#1a1820',
        },
        'sf-accent': {
          cyan: '#67e8f9',
          magenta: '#f472b6',
          gold: '#fbbf24',
          purple: '#a78bfa',
          blue: '#60a5fa',
        },
        'sf-text': {
          primary: '#f5f3fa',
          secondary: '#a9a4b5',
          muted: '#6b6778',
        },
        'sf-status': {
          success: '#34d399',
          warning: '#fbbf24',
          error: '#f87171',
          pending: '#fbbf24',
          running: '#67e8f9',
          completed: '#34d399',
          failed: '#f87171',
        },
        'sf-border': '#24222c',
      },
      fontFamily: {
        // Display - Dramatic serif for headings
        display: ['Playfair Display', 'Georgia', 'serif'],
        // Body - Clean, readable sans
        body: ['DM Sans', 'system-ui', 'sans-serif'],
        // Mono - Technical/code font
        mono: ['IBM Plex Mono', 'Consolas', 'monospace'],
        // Condensed - For labels and badges
        condensed: ['Barlow Condensed', 'sans-serif'],
      },
      fontSize: {
        // Custom fluid scale
        '2xs': ['0.625rem', { lineHeight: '1rem' }],
        'hero': ['4.5rem', { lineHeight: '1', letterSpacing: '-0.02em' }],
        'display': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'title': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
      },
      boxShadow: {
        // Glow effects
        'glow-rose': '0 0 40px rgba(204, 122, 90, 0.3)',
        'glow-rose-sm': '0 0 20px rgba(204, 122, 90, 0.25)',
        'glow-amber': '0 0 40px rgba(212, 165, 116, 0.3)',
        'glow-violet': '0 0 40px rgba(139, 92, 246, 0.3)',
        'glow-cyan': '0 0 20px rgba(103, 232, 249, 0.4)',
        'glow-success': '0 0 20px rgba(52, 211, 153, 0.4)',

        // Card shadows
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2)',
        'card-hover': '0 20px 40px -15px rgba(204, 122, 90, 0.15), 0 8px 16px -8px rgba(0, 0, 0, 0.3)',
        'card-elevated': '0 25px 50px -12px rgba(0, 0, 0, 0.5)',

        // Inner shadows for depth
        'inner-glow': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.05)',
        'inner-dark': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.3)',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      backgroundImage: {
        // Gradient meshes
        'mesh-rose': 'radial-gradient(at 40% 20%, rgba(204, 122, 90, 0.15) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(139, 92, 246, 0.1) 0px, transparent 50%), radial-gradient(at 0% 50%, rgba(201, 162, 39, 0.1) 0px, transparent 50%)',
        'mesh-ambient': 'radial-gradient(ellipse at top, rgba(139, 92, 246, 0.05) 0%, transparent 50%), radial-gradient(ellipse at bottom, rgba(204, 122, 90, 0.05) 0%, transparent 50%)',

        // Noise texture overlay
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",

        // Gradients
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-rose': 'linear-gradient(135deg, #cc7a5a 0%, #d4a574 50%, #c9a227 100%)',
        'gradient-violet': 'linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%)',
        'gradient-dark': 'linear-gradient(180deg, #121117 0%, #08070a 100%)',
      },
      animation: {
        // Entrance animations
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'fade-in-up': 'fadeInUp 0.6s ease-out forwards',
        'fade-in-down': 'fadeInDown 0.6s ease-out forwards',
        'slide-in-left': 'slideInLeft 0.5s ease-out forwards',
        'slide-in-right': 'slideInRight 0.5s ease-out forwards',
        'scale-in': 'scaleIn 0.4s ease-out forwards',

        // Looping animations
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'pulse-soft': 'pulseSoft 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'spin-slow': 'spin 8s linear infinite',
        'spin-slower': 'spin 20s linear infinite',
        'gradient-shift': 'gradientShift 8s ease infinite',

        // Waveform animation
        'wave-1': 'wave 1.2s ease-in-out infinite',
        'wave-2': 'wave 1.2s ease-in-out 0.1s infinite',
        'wave-3': 'wave 1.2s ease-in-out 0.2s infinite',
        'wave-4': 'wave 1.2s ease-in-out 0.3s infinite',
        'wave-5': 'wave 1.2s ease-in-out 0.4s infinite',

        // LED pulse
        'led-pulse': 'ledPulse 1.5s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-30px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(30px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px rgba(204, 122, 90, 0.3)' },
          '50%': { opacity: '0.8', boxShadow: '0 0 40px rgba(204, 122, 90, 0.5)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        wave: {
          '0%, 100%': { height: '20%', opacity: '0.5' },
          '50%': { height: '100%', opacity: '1' },
        },
        ledPulse: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.6', transform: 'scale(0.95)' },
        },
      },
      transitionTimingFunction: {
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
