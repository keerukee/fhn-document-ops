/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        fhn: {
          navy: '#002D72',
          red: '#E81C2D',
          gray: '#F3F4F6',
          dark: '#1F2937'
        }
      }
    },
  },
  plugins: [],
}
