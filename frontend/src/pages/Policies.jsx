import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useForm } from 'react-hook-form';

const Policies = () => {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState(null);
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const response = await axios.get('/api/shadow/policies');
      setPolicies(response.data);
    } catch (error) {
      console.error('Error fetching policies:', error);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      if (editingPolicy) {
        await axios.put(`/api/shadow/policies/${editingPolicy.id}`, data);
      } else {
        await axios.post('/api/shadow/policies', data);
      }
      setShowModal(false);
      setEditingPolicy(null);
      reset();
      fetchPolicies();
    } catch (error) {
      console.error('Error saving policy:', error);
      alert('保存策略失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleEdit = (policy) => {
    setEditingPolicy(policy);
    reset(policy);
    setShowModal(true);
  };

  const handleDelete = async (policyId) => {
    if (!confirm('确定要删除这个策略吗？')) return;
    
    try {
      await axios.delete(`/api/shadow/policies/${policyId}`);
      fetchPolicies();
    } catch (error) {
      console.error('Error deleting policy:', error);
      alert('删除策略失败');
    }
  };

  const handleInitializeDefaults = async () => {
    if (!confirm('确定要初始化默认策略吗？这将创建一组推荐的安全策略。')) return;
    
    try {
      await axios.post('/api/shadow/policies/initialize-defaults');
      fetchPolicies();
      alert('默认策略已创建');
    } catch (error) {
      console.error('Error initializing defaults:', error);
      alert('初始化默认策略失败');
    }
  };

  const getActionColor = (action) => {
    const colors = {
      allow: 'text-green-400 bg-green-500/20 border-green-500/30',
      deny: 'text-red-400 bg-red-500/20 border-red-500/30',
      audit: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
      quarantine: 'text-orange-400 bg-orange-500/20 border-orange-500/30'
    };
    return colors[action] || 'text-gray-400 bg-gray-500/20 border-gray-500/30';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-accent-blue border-t-transparent rounded-full animate-spin"></div>
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
        <div>
          <h1 className="text-3xl font-bold text-white">安全策略</h1>
          <p className="text-gray-400 mt-2">配置AI Agent的网络访问策略</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleInitializeDefaults}
            className="px-4 py-2 bg-dark-400 text-gray-300 rounded-lg hover:bg-dark-300 transition-colors"
          >
            初始化默认策略
          </button>
          <button
            onClick={() => {
              setEditingPolicy(null);
              reset();
              setShowModal(true);
            }}
            className="px-4 py-2 bg-accent-blue text-white rounded-lg hover:bg-accent-blue/80 transition-colors"
          >
            新建策略
          </button>
        </div>
      </motion.div>

      {/* 策略列表 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4"
      >
        {policies.length === 0 ? (
          <div className="bg-primary-module rounded-xl p-8 text-center border border-dark-300">
            <p className="text-gray-400">暂无策略，请创建新策略或初始化默认策略</p>
          </div>
        ) : (
          policies.map((policy) => (
            <div
              key={policy.id}
              className="bg-primary-module rounded-xl p-6 border border-dark-300 hover:border-accent-blue/50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-white">{policy.name}</h3>
                    <span className={`px-2 py-1 rounded text-xs border ${getActionColor(policy.action)}`}>
                      {policy.action}
                    </span>
                    {!policy.is_active && (
                      <span className="px-2 py-1 rounded text-xs bg-gray-500/20 text-gray-400 border border-gray-500/30">
                        已禁用
                      </span>
                    )}
                  </div>
                  <p className="text-gray-400 text-sm mb-3">{policy.description}</p>
                  <div className="flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center text-gray-300">
                      <span className="text-gray-500 mr-2">资源类型:</span>
                      {policy.resource_type}
                    </div>
                    <div className="flex items-center text-gray-300">
                      <span className="text-gray-500 mr-2">匹配模式:</span>
                      <code className="bg-dark-400 px-2 py-1 rounded text-xs">{policy.resource_pattern}</code>
                    </div>
                    <div className="flex items-center text-gray-300">
                      <span className="text-gray-500 mr-2">优先级:</span>
                      {policy.priority}
                    </div>
                    <div className="flex items-center text-gray-300">
                      <span className="text-gray-500 mr-2">风险阈值:</span>
                      {policy.risk_threshold}
                    </div>
                    {policy.enable_intent_audit && (
                      <div className="flex items-center text-accent-blue">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        意图审计
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex space-x-2 ml-4">
                  <button
                    onClick={() => handleEdit(policy)}
                    className="p-2 text-gray-400 hover:text-accent-blue transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(policy.id)}
                    className="p-2 text-gray-400 hover:text-accent-pink transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </motion.div>

      {/* 新建/编辑策略模态框 */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-primary-module rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-dark-300"
          >
            <div className="p-6 border-b border-dark-300">
              <h2 className="text-xl font-bold text-white">
                {editingPolicy ? '编辑策略' : '新建策略'}
              </h2>
            </div>
            
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">策略名称</label>
                <input
                  {...register('name', { required: '请输入策略名称' })}
                  className="w-full input-dark"
                  placeholder="例如：禁止访问内部网络"
                />
                {errors.name && <p className="text-accent-pink text-sm mt-1">{errors.name.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">描述</label>
                <textarea
                  {...register('description')}
                  className="w-full input-dark"
                  rows={2}
                  placeholder="策略的详细描述"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">资源类型</label>
                  <select {...register('resource_type', { required: true })} className="w-full input-dark">
                    <option value="api">API接口</option>
                    <option value="database">数据库</option>
                    <option value="file">文件系统</option>
                    <option value="network">网络</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">动作</label>
                  <select {...register('action', { required: true })} className="w-full input-dark">
                    <option value="allow">允许</option>
                    <option value="deny">拒绝</option>
                    <option value="audit">审计</option>
                    <option value="quarantine">隔离</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">资源匹配模式</label>
                <input
                  {...register('resource_pattern', { required: '请输入匹配模式' })}
                  className="w-full input-dark"
                  placeholder="例如：*.internal.com 或 /api/admin/*"
                />
                <p className="text-xs text-gray-500 mt-1">支持通配符 * 和正则表达式</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">风险阈值</label>
                  <select {...register('risk_threshold')} className="w-full input-dark">
                    <option value="low">低</option>
                    <option value="medium">中</option>
                    <option value="high">高</option>
                    <option value="critical">严重</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">优先级</label>
                  <input
                    type="number"
                    {...register('priority', { valueAsNumber: true })}
                    className="w-full input-dark"
                    placeholder="数字越小优先级越高"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  {...register('enable_intent_audit')}
                  className="w-4 h-4 rounded border-gray-600 bg-dark-400 text-accent-blue focus:ring-accent-blue"
                />
                <label className="text-sm text-gray-300">启用意图审计</label>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  {...register('is_active')}
                  className="w-4 h-4 rounded border-gray-600 bg-dark-400 text-accent-blue focus:ring-accent-blue"
                />
                <label className="text-sm text-gray-300">启用策略</label>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingPolicy(null);
                    reset();
                  }}
                  className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-accent-blue text-white rounded-lg hover:bg-accent-blue/80 transition-colors"
                >
                  {editingPolicy ? '保存' : '创建'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Policies;
