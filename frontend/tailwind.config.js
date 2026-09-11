/** Design tokens (UI brief §2) mapped onto the Organic palette. */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        surface: '#f5ead8',
        'surface-raised': '#ebddc5',
        'border-default': '#dcd3c4',
        'text-primary': '#201e1d',
        'text-secondary': '#645c50',
        available: '#8fa073',
        'available-hover': '#728157',
        'too-small': '#dcd3c4',
        reserved: '#d67f48',
        accent: '#c67139',
        'accent-hover': '#b2622d',
        'accent-press': '#8c491a',
        'accent-tint': '#fff2eb',
        'accent-tint-strong': '#ffe1d0',
        danger: '#8c491a',
        'warning-surface': '#fff2eb',
        'warning-text': '#643312',
        neutral: {
          100: '#f9f4ed',
          200: '#eee7db',
          300: '#dcd3c4',
          400: '#c0b6a5',
          600: '#82796a',
          800: '#474238',
          900: '#2e2b25'
        },
        sage: {
          100: '#f0fae1',
          500: '#8fa073',
          600: '#728157',
          800: '#3d472b'
        }
      },
      fontFamily: {
        display: ['Caprasimo', 'system-ui', 'sans-serif'],
        body: ['Figtree', 'system-ui', 'sans-serif']
      },
      borderRadius: {
        card: '32px',
        cell: '28px',
        field: '999px'
      },
      boxShadow: {
        md: '0 3px 10px rgba(46, 43, 37, 0.16)',
        lg: '0 12px 32px rgba(46, 43, 37, 0.22)',
        xl: '0 12px 32px rgba(46, 43, 37, 0.28)'
      },
      keyframes: {
        'pop-in': { from: { transform: 'scale(0.2)', opacity: '0' }, to: { transform: 'scale(1)', opacity: '1' } },
        'fade-swap': { from: { opacity: '0.25' }, to: { opacity: '1' } },
        'pulse-cell': { '0%,100%': { opacity: '0.5' }, '50%': { opacity: '0.28' } },
        shake: {
          '0%,100%': { transform: 'translateX(0)' },
          '20%': { transform: 'translateX(-6px)' },
          '40%': { transform: 'translateX(5px)' },
          '60%': { transform: 'translateX(-3px)' },
          '80%': { transform: 'translateX(2px)' }
        },
        'check-pop': {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '60%': { transform: 'scale(1.12)', opacity: '1' },
          '100%': { transform: 'scale(1)', opacity: '1' }
        }
      },
      animation: {
        'pop-in': 'pop-in 220ms ease-out',
        'fade-swap': 'fade-swap 200ms ease-out',
        'pulse-cell': 'pulse-cell 1.1s ease-in-out infinite',
        shake: 'shake 300ms ease-in-out',
        'check-pop': 'check-pop 420ms ease-out'
      }
    }
  },
  plugins: []
}
