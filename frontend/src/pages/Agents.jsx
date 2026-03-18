import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [error, setError] = useState('');
  const [newAgent, setNewAgent] = useState({
    name: '',
    description: '',
    agent_type: 'DeepSeek',
    model_id: 'deepseek-chat',
    config_json: {
      temperature: 0.7
    }
  });

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('/api/agents', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setAgents(response.data);
      } catch (error) {
        console.error('Error fetching agents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  const handleCreateAgent = async () => {
    // 验证输入
    if (!newAgent.name.trim()) {
      setError('请输入代理名称');
      return;
    }

    setCreateLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      console.log('Token from localStorage:', token ? token.substring(0, 20) + '...' : 'null');
      
      if (!token) {
        setError('未登录，请先登录');
        setCreateLoading(false);
        return;
      }
      
      console.log('Creating agent:', newAgent);
      const response = await axios.post('/api/agents', newAgent, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('Agent created:', response.data);
      setAgents([...agents, response.data]);
      setIsModalOpen(false);
      setNewAgent({
        name: '',
        description: '',
        agent_type: 'DeepSeek',
        model_id: 'deepseek-chat',
        config_json: {
          temperature: 0.7
        }
      });
    } catch (error) {
      console.error('Error creating agent:', error);
      console.error('Error response:', error.response);
      console.error('Error request:', error.request);
      const errorMsg = error.response?.data?.detail || error.message || '创建代理失败';
      setError(errorMsg);
    } finally {
      setCreateLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <h1 className="text-3xl font-bold text-white">AI 代理</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="gradient-bg text-white px-6 py-2 rounded-lg font-medium btn-primary shadow-neon-blue"
        >
          创建代理
        </button>
      </motion.div>

      {/* Agents Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {agents.map((agent) => (
          <motion.div
            key={agent.id}
            className="bg-primary-module rounded-xl shadow-lg overflow-hidden card-hover tech-border"
            whileHover={{ y: -5 }}
            transition={{ duration: 0.2 }}
          >
            <div className="gradient-bg p-6 text-white">
              <h3 className="text-xl font-bold">{agent.name}</h3>
              <p className="opacity-90 text-sm mt-1">{agent.agent_type} - {agent.model_id}</p>
            </div>
            <div className="p-6">
              <p className="text-gray-300 mb-4">{agent.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">
                  温度: {agent.config_json?.temperature || 0.7}
                </span>
                <div className="flex space-x-2">
                  <button className="text-accent-blue hover:text-accent-purple transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 0H17a2 2 0 012 2v8a2 2 0 01-2 2H6a2 2 0 01-2-2V5a2 2 0 012-2h11a4 4 0 004 4v-1" />
                    </svg>
                  </button>
                  <button className="text-accent-pink hover:text-accent-blue transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6M4 7v6a1 1 0 001 1h14a1 1 0 001-1V7a1 1 0 00-1-1h-4" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Create Agent Modal */}
      {isModalOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-primary-module rounded-xl shadow-2xl w-full max-w-md p-6 tech-border"
          >
            <h2 className="text-2xl font-bold text-white mb-4">创建新代理</h2>
            
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-accent-pink/20 text-accent-pink p-3 rounded-lg mb-4 border border-accent-pink/30"
              >
                {error}
              </motion.div>
            )}
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  名称 <span className="text-accent-pink">*</span>
                </label>
                <input
                  type="text"
                  value={newAgent.name}
                  onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                  className="input-dark w-full px-4 py-2 rounded-lg"
                  placeholder="代理名称"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  描述
                </label>
                <textarea
                  value={newAgent.description}
                  onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
                  className="input-dark w-full px-4 py-2 rounded-lg"
                  placeholder="代理描述"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  模型
                </label>
                <select
                  value={newAgent.model_id}
                  onChange={(e) => setNewAgent({ ...newAgent, model_id: e.target.value })}
                  className="input-dark w-full px-4 py-2 rounded-lg"
                >
                  <option value="deepseek-chat">DeepSeek Chat</option>
                  <option value="deepseek-code">DeepSeek Code</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  温度
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={newAgent.config_json.temperature}
                  onChange={(e) => setNewAgent({ 
                    ...newAgent, 
                    config_json: { 
                      ...newAgent.config_json, 
                      temperature: parseFloat(e.target.value) 
                    } 
                  })}
                  className="w-full"
                />
                <p className="text-sm text-gray-400 text-center mt-2">{newAgent.config_json.temperature}</p>
              </div>
            </div>
            
            <div className="flex space-x-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setError('');
                }}
                disabled={createLoading}
                className="flex-1 px-4 py-2 border border-dark-300 rounded-lg text-gray-300 hover:bg-dark-400 transition-colors disabled:opacity-50"
              >
                取消
              </button>
              <button
                onClick={handleCreateAgent}
                disabled={createLoading}
                className="flex-1 btn-primary gradient-bg text-white px-4 py-2 rounded-lg font-medium shadow-neon-blue disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {createLoading ? '创建中...' : '创建'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default Agents;
