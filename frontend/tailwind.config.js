/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#f4f7fe',
        card: '#ffffff',
        primary: '#4318ff',
        'primary-hover': '#3210cc',
        success: '#05cd99',
        'success-light': '#e6fbf4',
        warning: '#ffb547',
        'warning-light': '#fff7eb',
        info: '#39b8ff',
        'info-light': '#eaf7ff',
        purple: '#868cff',
        'purple-light': '#f4f5ff',
        pink: '#ff65a0',
        'pink-light': '#ffeff5',
        sidebar: '#12182b',
        'text-main': '#2b3674',
        'text-muted': '#a3aed1',
        border: '#e9edf7',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        card: '0px 4px 18px rgba(0, 0, 0, 0.05)',
      }
    },
  },
  plugins: [],
}
