/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        agent: {
          primary: "var(--agent-primary)",
          secondary: "var(--agent-secondary)",
        }
      }
    },
  },
  plugins: [],
}
