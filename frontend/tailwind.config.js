/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 主色调
        primary: {
          background: '#0A0A0A',  // 主背景：极深灰/近黑
          module: '#1A1A2E',      // 深层模块背景：深蓝紫
        },
        
        // 辅助色
        accent: {
          blue: '#00BCD4',      // 科技蓝：亮青色
          purple: '#8854D9',     // 幻影紫：中等紫色
          pink: '#FF6D99',       // 霓虹粉：亮粉色
        },
        
        // 霓虹色
        neon: {
          cyan: '#00f5d4',      // 荧光青
          blue: '#00d4ff',       // 霓虹蓝
          purple: '#9933ff',     // 霓虹紫
          indigo: '#3a0ca3',     // 靛蓝
        },
        
        // 深色渐变
        deep: {
          purple: '#120458',     // 深紫
          dark: '#0a032e',       // 深黑
          blue: '#16213e',       // 深蓝
        },
        
        // 浅色文字
        light: {
          white: '#f8f9fa',     // 亮白
          purple: '#e0aaff',     // 浅紫
        },
        
        // 扩展颜色
        dark: {
          50: '#0A0A0A',
          100: '#1A1A2E',
          200: '#2D2D44',
          300: '#40405A',
          400: '#535371',
          500: '#666688',
          600: '#79799F',
          700: '#8C8CB6',
          800: '#9F9FCD',
          900: '#B2B2E4',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'gradient-flow': 'gradientFlow 8s ease infinite',
        'card-breath': 'cardBreath 5s ease infinite',
        'card-enter': 'cardEnter 0.8s ease-out forwards',
        'float': 'float 15s infinite ease-in-out',
        'btn-gradient': 'btnGradient 3s ease infinite',
        'text-fade-in': 'textFadeIn 0.5s ease forwards',
        'bounce-light': 'bounceLight 0.3s ease',
        'slide-in-right': 'slideInRight 0.6s ease forwards',
        'progress-pulse': 'progressPulse 0.5s ease',
      },
      keyframes: {
        glow: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        gradientFlow: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        cardBreath: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        cardEnter: {
          '0%': { 
            opacity: '0',
            transform: 'translateY(50px) scale(0.9) rotate(-3deg)' 
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0) scale(1) rotate(0deg)' 
          },
        },
        float: {
          '0%, 100%': {
            transform: 'translateY(0) translateX(0)',
            opacity: '0.6',
          },
          '25%': {
            transform: 'translateY(-20px) translateX(10px)',
            opacity: '0.8',
          },
          '50%': {
            transform: 'translateY(-10px) translateX(-10px)',
            opacity: '0.4',
          },
          '75%': {
            transform: 'translateY(-30px) translateX(5px)',
            opacity: '0.7',
          },
        },
        btnGradient: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        textFadeIn: {
          'from': {
            opacity: '0',
            transform: 'translateY(10px)',
          },
          'to': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        bounceLight: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        slideInRight: {
          'from': {
            opacity: '0',
            transform: 'translateX(20px)',
          },
          'to': {
            opacity: '1',
            transform: 'translateX(0)',
          },
        },
        progressPulse: {
          '0%': { opacity: '0.5' },
          '50%': { opacity: '1' },
          '100%': { opacity: '0.5' },
        },
      },
      boxShadow: {
        'neon-blue': '0 0 5px #00BCD4, 0 0 20px #00BCD4',
        'neon-purple': '0 0 5px #8854D9, 0 0 20px #8854D9',
        'neon-pink': '0 0 5px #FF6D99, 0 0 20px #FF6D99',
        'neon-cyan': '0 0 20px rgba(0, 245, 212, 0.5)',
        'glow-cyan': '0 0 30px rgba(0, 245, 212, 0.5)',
      },
    },
  },
  plugins: [],
}
