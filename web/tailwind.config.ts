import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    colors: {
      'white': '#ffffff',
      'slate': {
        '50': '#f9f9f9',
        '100': '#f0f0f0',
        '200': '#e5e5e5',
        '300': '#d5d5d5',
        '400': '#999999',
        '500': '#666666',
        '600': '#666666',
        '700': '#666666',
        '800': '#1a1a1a',
        '900': '#1a1a1a',
      },
      'blue': {
        '50': '#f0f4ff',
        '600': '#0052cc',
        '700': '#0a3399',
      },
      'green': {
        '400': '#27ae60',
        '600': '#27ae60',
        '700': '#27ae60',
      },
      'red': {
        '500': '#ff5f57',
        '600': '#ff5f57',
      },
      'amber': {
        '500': '#febc2e',
        '600': '#febc2e',
      },
      'emerald': {
        '400': '#27ae60',
        '950': '#1a4d2e',
      },
      'indigo': {
        '400': '#0052cc',
        '600': '#0052cc',
      },
    }
  },
} satisfies Config
