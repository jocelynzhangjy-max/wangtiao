import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import useAuthStore from '../stores/authStore';

const Dashboard = () => {
  const [stats, setStats] = useState({
    agents: 0,
    conversations: 0,
    tools: 0
  });
  const [recentConversations, setRecentConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated, checkAuth } = useAuthStore();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // 先检查认证状态
        if (!isAuthenticated) {
          await checkAuth();
        }

        // 获取统计数据
        const [agentsResponse, conversationsResponse, toolsResponse] = await Promise.all([
          axios.get('/api/agents'),
          axios.get('/api/conversations'),
          axios.get('/api/tools')
        ]);

        setStats({
          agents: agentsResponse.data.length,
          conversations: conversationsResponse.data.length,
          tools: toolsResponse.data.length
        });

        // 获取最近的对话
        const conversations = conversationsResponse.data
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 5);
        setRecentConversations(conversations);
      } catch (error) {
        console.error('Error fetching stats:', error);
        // 如果是401错误，尝试重新检查认证状态
        if (error.response?.status === 401) {
          await checkAuth();
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [isAuthenticated, checkAuth]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-white">仪表盘</h1>
        <p className="text-gray-400 mt-2">欢迎来到您的 AI Agent Gateway 仪表盘</p>
      </motion.div>

      {/* 统计卡片 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        <div className="bg-primary-module rounded-xl shadow-lg p-6 card-hover tech-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">AI 代理总数</p>
              <h3 className="text-3xl font-bold text-white mt-2">{stats.agents}</h3>
            </div>
            <div className="w-12 h-12 bg-accent-blue/20 rounded-full flex items-center justify-center border border-accent-blue/30">
              <svg className="w-6 h-6 text-accent-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-primary-module rounded-xl shadow-lg p-6 card-hover tech-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">对话总数</p>
              <h3 className="text-3xl font-bold text-white mt-2">{stats.conversations}</h3>
            </div>
            <div className="w-12 h-12 bg-accent-purple/20 rounded-full flex items-center justify-center border border-accent-purple/30">
              <svg className="w-6 h-6 text-accent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-primary-module rounded-xl shadow-lg p-6 card-hover tech-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">工具总数</p>
              <h3 className="text-3xl font-bold text-white mt-2">{stats.tools}</h3>
            </div>
            <div className="w-12 h-12 bg-accent-pink/20 rounded-full flex items-center justify-center border border-accent-pink/30">
              <svg className="w-6 h-6 text-accent-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
          </div>
        </div>
      </motion.div>

      {/* 最近对话 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <h2 className="text-xl font-bold text-white mb-4">最近对话</h2>
        <div className="bg-primary-module rounded-xl shadow-lg p-6 tech-border">
          {recentConversations.length === 0 ? (
            <p className="text-gray-400">暂无对话记录</p>
          ) : (
            <div className="space-y-4">
              {recentConversations.map((conversation) => (
                <div key={conversation.id} className="flex items-center justify-between p-3 hover:bg-dark-400 rounded-lg transition-colors">
                  <div>
                    <h3 className="text-white font-medium">{conversation.agent_name || 'AI Agent'}</h3>
                    <p className="text-gray-400 text-sm mt-1">
                      {conversation.last_message || '无消息'}
                    </p>
                  </div>
                  <div className="text-gray-400 text-sm">
                    {new Date(conversation.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
