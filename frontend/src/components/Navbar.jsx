import React from 'react';
import { motion } from 'framer-motion';

const Navbar = ({ title, onLogout, onPageChange }) => {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-primary-module shadow-md px-6 py-4 sticky top-0 z-10 border-b border-dark-300"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-gradient-to-br from-accent-blue to-accent-purple rounded-lg flex items-center justify-center mr-3 shadow-neon-blue">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white">{title}</h1>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="relative">
            <input
              type="text"
              placeholder="搜索..."
              className="input-dark pl-10 pr-4 py-2 rounded-lg w-64"
            />
            <svg className="absolute left-3 top-3 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="relative p-2 rounded-full hover:bg-dark-400 transition-colors">
              <svg className="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span className="absolute top-1 right-1 w-2 h-2 bg-accent-pink rounded-full shadow-neon-pink"></span>
            </button>
            
            <div className="relative group">
              <button className="flex items-center space-x-2 focus:outline-none">
                <div className="w-10 h-10 bg-dark-400 rounded-full flex items-center justify-center border border-accent-blue">
                  <span className="text-white font-medium">U</span>
                </div>
                <span className="text-gray-300 font-medium">用户</span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              <div className="absolute right-0 mt-2 w-48 bg-primary-module rounded-lg shadow-xl py-2 z-20 hidden group-hover:block border border-dark-300">
                <button className="block w-full text-left px-4 py-2 text-gray-300 hover:bg-dark-400 hover:text-accent-blue transition-colors">
                  个人资料
                </button>
                <button className="block w-full text-left px-4 py-2 text-gray-300 hover:bg-dark-400 hover:text-accent-blue transition-colors">
                  设置
                </button>
                <div className="border-t border-dark-300 my-1"></div>
                <button 
                  onClick={onLogout}
                  className="block w-full text-left px-4 py-2 text-accent-pink hover:bg-dark-400 transition-colors"
                >
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
