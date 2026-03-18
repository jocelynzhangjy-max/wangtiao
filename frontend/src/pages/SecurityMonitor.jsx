import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const SecurityMonitor = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [reputationData, setReputationData] = useState(null);
  const [behaviorReport, setBehaviorReport] = useState(null);
  const [reputationSummary, setReputationSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 获取所有智能体
  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/agents', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setAgents(response.data);
    } catch (err) {
      setError('获取智能体列表失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 获取智能体信誉评分
  const fetchAgentReputation = async (agentId) => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:8000/api/reputation/agents/${agentId}/reputation`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setReputationData(response.data);
    } catch (err) {
      setError('获取信誉评分失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 获取智能体行为报告
  const fetchAgentBehaviorReport = async (agentId) => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:8000/api/reputation/agents/${agentId}/behavior-report`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setBehaviorReport(response.data);
    } catch (err) {
      setError('获取行为报告失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 获取信誉摘要
  const fetchReputationSummary = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/reputation/summary', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setReputationSummary(response.data);
    } catch (err) {
      setError('获取信誉摘要失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 刷新智能体信誉评分
  const refreshAgentReputation = async (agentId) => {
    try {
      setLoading(true);
      const response = await axios.post(`http://localhost:8000/api/reputation/agents/${agentId}/reputation/refresh`, {}, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setReputationData(response.data.reputation);
    } catch (err) {
      setError('刷新信誉评分失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 选择智能体
  const handleSelectAgent = (agent) => {
    setSelectedAgent(agent);
    fetchAgentReputation(agent.id);
    fetchAgentBehaviorReport(agent.id);
  };

  useEffect(() => {
    fetchAgents();
    fetchReputationSummary();
  }, []);

  // 计算信誉评分等级和颜色
  const getReputationLevel = (score) => {
    if (score >= 80) return { level: '优秀', color: 'text-green-400' };
    if (score >= 60) return { level: '良好', color: 'text-yellow-400' };
    if (score >= 40) return { level: '一般', color: 'text-orange-400' };
    return { level: '较差', color: 'text-red-400' };
  };

  return (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-dark-200 rounded-xl p-6 border border-accent-blue/20 shadow-lg"
      >
        <h2 className="text-2xl font-bold text-accent-blue mb-4">安全监控中心</h2>
        <p className="text-gray-300 mb-6">监控智能体行为，评估信誉风险</p>

        {/* 信誉摘要 */}
        {reputationSummary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
              <div className="text-gray-400 text-sm mb-1">总智能体数</div>
              <div className="text-2xl font-bold text-white">{reputationSummary.total_agents}</div>
            </div>
            <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
              <div className="text-gray-400 text-sm mb-1">平均信誉评分</div>
              <div className="text-2xl font-bold text-white">{reputationSummary.average_reputation_score.toFixed(1)}</div>
            </div>
            <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
              <div className="text-gray-400 text-sm mb-1">最佳智能体</div>
              <div className="text-lg font-semibold text-white">{reputationSummary.top_performers[0]?.agent_name || '无'}</div>
              <div className="text-sm text-green-400">{reputationSummary.top_performers[0]?.total_score.toFixed(1) || '0'}</div>
            </div>
            <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
              <div className="text-gray-400 text-sm mb-1">需关注智能体</div>
              <div className="text-lg font-semibold text-white">{reputationSummary.low_performers[0]?.agent_name || '无'}</div>
              <div className="text-sm text-red-400">{reputationSummary.low_performers[0]?.total_score.toFixed(1) || '0'}</div>
            </div>
          </div>
        )}

        {/* 智能体列表 */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-white mb-4">智能体安全状态</h3>
          <div className="bg-dark-300 rounded-lg overflow-hidden">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 px-4 py-3 border-b border-dark-400 text-sm font-medium text-gray-400">
              <div>智能体</div>
              <div>类型</div>
              <div>信誉评分</div>
              <div>风险等级</div>
            </div>
            {agents.map((agent) => {
              const level = getReputationLevel(agent.trust_level || 50);
              return (
                <motion.div
                  key={agent.id}
                  whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
                  className={`grid grid-cols-1 md:grid-cols-4 gap-4 px-4 py-3 border-b border-dark-400 items-center cursor-pointer ${selectedAgent?.id === agent.id ? 'bg-dark-400' : ''}`}
                  onClick={() => handleSelectAgent(agent)}
                >
                  <div className="text-white font-medium">{agent.name}</div>
                  <div className="text-gray-300">{agent.agent_type}</div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-dark-400 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${level.color}`}
                        style={{ width: `${Math.min(agent.trust_level || 50, 100)}%` }}
                      ></div>
                    </div>
                    <span className={level.color}>{agent.trust_level || 50}</span>
                  </div>
                  <div>
                    <span className={`px-2 py-1 rounded-full text-xs ${level.color}`}>
                      {level.level}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* 智能体详情 */}
      {selectedAgent && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-dark-200 rounded-xl p-6 border border-accent-blue/20 shadow-lg"
        >
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold text-white">{selectedAgent.name} - 安全详情</h3>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => refreshAgentReputation(selectedAgent.id)}
              disabled={loading}
              className="bg-accent-blue hover:bg-accent-blue/80 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {loading ? '刷新中...' : '刷新评分'}
            </motion.button>
          </div>

          {/* 信誉评分详情 */}
          {reputationData && (
            <div className="mb-8">
              <h4 className="text-lg font-medium text-gray-300 mb-4">信誉评分详情</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
                  <div className="text-gray-400 text-sm mb-1">总评分</div>
                  <div className="text-3xl font-bold text-white">{reputationData.total_score.toFixed(1)}</div>
                  <div className="text-xs text-gray-500 mt-1">{new Date(reputationData.last_updated).toLocaleString()}</div>
                </div>
                <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
                  <div className="text-gray-400 text-sm mb-1">安全合规性</div>
                  <div className="text-2xl font-bold text-white">{reputationData.security_score.toFixed(1)}</div>
                  <div className="w-full bg-dark-400 rounded-full h-1.5 mt-2">
                    <div 
                      className="bg-green-400 h-1.5 rounded-full"
                      style={{ width: `${reputationData.security_score}%` }}
                    ></div>
                  </div>
                </div>
                <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
                  <div className="text-gray-400 text-sm mb-1">协作成功率</div>
                  <div className="text-2xl font-bold text-white">{reputationData.collaboration_score.toFixed(1)}</div>
                  <div className="w-full bg-dark-400 rounded-full h-1.5 mt-2">
                    <div 
                      className="bg-blue-400 h-1.5 rounded-full"
                      style={{ width: `${reputationData.collaboration_score}%` }}
                    ></div>
                  </div>
                </div>
                <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
                  <div className="text-gray-400 text-sm mb-1">资源使用效率</div>
                  <div className="text-2xl font-bold text-white">{reputationData.resource_score.toFixed(1)}</div>
                  <div className="w-full bg-dark-400 rounded-full h-1.5 mt-2">
                    <div 
                      className="bg-yellow-400 h-1.5 rounded-full"
                      style={{ width: `${reputationData.resource_score}%` }}
                    ></div>
                  </div>
                </div>
                <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
                  <div className="text-gray-400 text-sm mb-1">响应质量</div>
                  <div className="text-2xl font-bold text-white">{reputationData.response_score.toFixed(1)}</div>
                  <div className="w-full bg-dark-400 rounded-full h-1.5 mt-2">
                    <div 
                      className="bg-purple-400 h-1.5 rounded-full"
                      style={{ width: `${reputationData.response_score}%` }}
                    ></div>
                  </div>
                </div>
                <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
                  <div className="text-gray-400 text-sm mb-1">行为一致性</div>
                  <div className="text-2xl font-bold text-white">{reputationData.consistency_score.toFixed(1)}</div>
                  <div className="w-full bg-dark-400 rounded-full h-1.5 mt-2">
                    <div 
                      className="bg-pink-400 h-1.5 rounded-full"
                      style={{ width: `${reputationData.consistency_score}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 行为分析报告 */}
          {behaviorReport && (
            <div>
              <h4 className="text-lg font-medium text-gray-300 mb-4">行为分析报告</h4>
              <div className="bg-dark-300 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div>
                    <div className="text-gray-400 text-sm mb-1">报告周期</div>
                    <div className="text-white">{behaviorReport.report_period}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm mb-1">总请求数</div>
                    <div className="text-white font-semibold">{behaviorReport.total_requests}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm mb-1">总告警数</div>
                    <div className="text-white font-semibold">{behaviorReport.total_alerts}</div>
                  </div>
                </div>

                {/* 异常行为 */}
                <div className="mb-6">
                  <h5 className="text-md font-medium text-white mb-3">异常行为</h5>
                  {behaviorReport.anomalies.length > 0 ? (
                    <div className="space-y-2">
                      {behaviorReport.anomalies.map((anomaly, index) => (
                        <div key={index} className="bg-dark-400 rounded-lg p-3 border-l-4 border-neon-pink">
                          <div className="flex justify-between items-start">
                            <div className="text-white font-medium">{anomaly.type}</div>
                            <div className="text-xs text-gray-400">{anomaly.timestamp}</div>
                          </div>
                          <div className="text-gray-300 text-sm mt-1">{anomaly.message}</div>
                          <div className="mt-2">
                            <span className={`px-2 py-0.5 rounded-full text-xs ${anomaly.severity === 'high' ? 'bg-red-900/30 text-red-400' : anomaly.severity === 'medium' ? 'bg-yellow-900/30 text-yellow-400' : 'bg-blue-900/30 text-blue-400'}`}>
                              {anomaly.severity}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-gray-400 text-sm">暂无异常行为</div>
                  )}
                </div>

                {/* 改进建议 */}
                <div>
                  <h5 className="text-md font-medium text-white mb-3">改进建议</h5>
                  {behaviorReport.recommendations.length > 0 ? (
                    <ul className="space-y-2">
                      {behaviorReport.recommendations.map((recommendation, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <svg className="w-5 h-5 text-accent-blue mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="text-gray-300">{recommendation}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="text-gray-400 text-sm">暂无建议</div>
                  )}
                </div>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* 错误提示 */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-4 right-4 bg-neon-pink/20 border border-neon-pink/50 text-neon-pink px-4 py-2 rounded-lg shadow-lg z-50"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SecurityMonitor;