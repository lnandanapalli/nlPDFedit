/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gray: {
          800: '#1f2937',
          900: '#111827',
        }
      },
      animation: {
        'bounce': 'bounce 1.4s infinite',
      }
    },
  },
  plugins: [],
}