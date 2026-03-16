import React, { useState } from 'react';
import { motion } from 'framer-motion';
import useAuthStore from '../stores/authStore';

const Settings = () => {
  const { user } = useAuthStore();
  const [settings, setSettings] = useState({
    theme: 'dark',
    notifications: true,
    language: 'zh',
    apiKey: ''
  });

  const handleSave = () => {
    console.log('设置已保存:', settings);
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-white">设置</h1>
        <p className="text-gray-400 mt-2">配置您的 AI Agent Gateway 设置</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="bg-primary-module rounded-xl shadow-lg p-6 tech-border"
      >
        <h2 className="text-xl font-semibold text-white mb-6">账户设置</h2>
        
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                用户名
              </label>
              <input
                type="text"
                value={user?.username || ''}
                className="input-dark w-full px-4 py-2 rounded-lg"
                disabled
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                邮箱
              </label>
              <input
                type="email"
                value={user?.email || ''}
                className="input-dark w-full px-4 py-2 rounded-lg"
                disabled
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              主题
            </label>
            <select
              value={settings.theme}
              onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
              className="input-dark w-full px-4 py-2 rounded-lg"
            >
              <option value="dark">深色</option>
              <option value="light">浅色</option>
              <option value="system">跟随系统</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              语言
            </label>
            <select
              value={settings.language}
              onChange={(e) => setSettings({ ...settings, language: e.target.value })}
              className="input-dark w-full px-4 py-2 rounded-lg"
            >
              <option value="zh">中文</option>
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
            </select>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="notifications"
              checked={settings.notifications}
              onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
              className="w-4 h-4 text-accent-blue focus:ring-accent-blue border-dark-300 rounded"
            />
            <label htmlFor="notifications" className="ml-2 block text-sm text-gray-300">
              启用通知
            </label>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              API 密钥
            </label>
            <input
              type="password"
              value={settings.apiKey}
              onChange={(e) => setSettings({ ...settings, apiKey: e.target.value })}
              className="input-dark w-full px-4 py-2 rounded-lg"
              placeholder="输入您的 API 密钥"
            />
            <p className="text-xs text-gray-400 mt-1">
              您的 API 密钥将被安全存储并用于代理交互
            </p>
          </div>
        </div>
        
        <div className="mt-8">
          <button
            onClick={handleSave}
            className="btn-primary gradient-bg text-white px-6 py-2 rounded-lg font-medium shadow-neon-blue"
          >
            保存设置
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default Settings;
