/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        coal: "#15171a",
        steel: "#26313d",
        copper: "#c47735",
        safety: "#f59e0b",
        minegreen: "#10b981",
        danger: "#ef4444"
      },
      boxShadow: {
        panel: "0 10px 30px rgba(21,23,26,.08)"
      }
    },
  },
  plugins: [],
}
