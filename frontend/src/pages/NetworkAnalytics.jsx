import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const NetworkAnalytics = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [timeWindow, setTimeWindow] = useState('day');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 获取仪表盘数据
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/analytics/dashboard', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setDashboardData(response.data);
    } catch (err) {
      setError('获取仪表盘数据失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 获取网络报告
  const fetchReportData = async () => {
    try {
      setLoading(true);
      const windowMap = {
        'hour': 3600,
        'day': 86400,
        'week': 604800
      };
      
      const response = await axios.get(`http://localhost:8000/api/analytics/report?time_window=${windowMap[timeWindow]}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setReportData(response.data);
    } catch (err) {
      setError('获取网络报告失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    fetchReportData();
  }, [timeWindow]);

  // 格式化数字
  const formatNumber = (num) => {
    return num.toLocaleString();
  };

  // 渲染风险等级颜色
  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  // 渲染时间分布图表
  const renderTimeDistribution = (data) => {
    if (!data || !data.time_distribution) return null;
    
    const hours = Array.from({ length: 24 }, (_, i) => i);
    const maxValue = Math.max(...Object.values(data.time_distribution), 1);
    
    return (
      <div className="h-64 w-full">
        <div className="flex items-end justify-between h-full px-2">
          {hours.map((hour) => (
            <div key={hour} className="flex flex-col items-center w-6">
              <div 
                className="w-4 bg-gradient-to-t from-accent-blue to-accent-purple rounded-t-sm transition-all duration-500"
                style={{ 
                  height: `${(data.time_distribution[hour] || 0) / maxValue * 100}%` 
                }}
              ></div>
              <span className="text-xs text-gray-400 mt-1">{hour}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-dark-200 rounded-xl p-6 border border-accent-blue/20 shadow-lg"
      >
        <h2 className="text-2xl font-bold text-accent-blue mb-4">网络数据分析</h2>
        <p className="text-gray-300 mb-6">分析智能体网络行为，识别异常模式</p>

        {/* 仪表盘概览 */}
        {dashboardData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
              <div className="text-gray-400 text-sm mb-1">总智能体数</div>
              <div className="text-2xl font-bold text-white">{dashboardData.summary.total_agents}</div>
            </div>
            <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
              <div className="text-gray-400 text-sm mb-1">今日请求数</div>
              <div className="text-2xl font-bold text-white">{formatNumber(dashboardData.summary.total_requests)}</div>
            </div>
            <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
              <div className="text-gray-400 text-sm mb-1">高风险智能体</div>
              <div className="text-2xl font-bold text-red-400">{dashboardData.summary.high_risk_agents}</div>
            </div>
            <div className="bg-dark-300 rounded-lg p-4 border border-accent-blue/30">
              <div className="text-gray-400 text-sm mb-1">平均风险分数</div>
              <div className="text-2xl font-bold text-white">{dashboardData.summary.average_risk_score.toFixed(1)}</div>
            </div>
          </div>
        )}

        {/* 时间窗口选择 */}
        <div className="flex gap-2 mb-6">
          {['hour', 'day', 'week'].map((window) => (
            <button
              key={window}
              onClick={() => setTimeWindow(window)}
              className={`px-4 py-2 rounded-lg transition-all ${timeWindow === window ? 'bg-accent-blue text-white' : 'bg-dark-300 text-gray-300 hover:bg-dark-400'}`}
            >
              {window === 'hour' ? '近1小时' : window === 'day' ? '近1天' : '近1周'}
            </button>
          ))}
        </div>

        {/* 网络流量分析 */}
        {reportData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* 流量概览 */}
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-dark-300 rounded-xl p-6 border border-accent-blue/30"
            >
              <h3 className="text-lg font-semibold text-white mb-4">流量概览</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-gray-300">总请求数</span>
                    <span className="text-white font-medium">{formatNumber(reportData.overall_analysis.total_requests)}</span>
                  </div>
                  <div className="w-full bg-dark-400 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full bg-accent-blue"
                      style={{ width: '100%' }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-gray-300">异常数量</span>
                    <span className="text-neon-pink font-medium">{reportData.overall_analysis.anomalies.length}</span>
                  </div>
                  <div className="w-full bg-dark-400 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full bg-neon-pink"
                      style={{ 
                        width: `${Math.min(reportData.overall_analysis.anomalies.length / 10 * 100, 100)}%` 
                      }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-gray-300">请求类型分布</span>
                  </div>
                  <div className="space-y-2">
                    {Object.entries(reportData.overall_analysis.request_types).map(([type, count]) => (
                      <div key={type}>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm text-gray-400">{type}</span>
                          <span className="text-sm text-white">{count}</span>
                        </div>
                        <div className="w-full bg-dark-400 rounded-full h-1.5">
                          <div 
                            className="h-1.5 rounded-full bg-gradient-to-r from-accent-blue to-accent-purple"
                            style={{ 
                              width: `${count / reportData.overall_analysis.total_requests * 100}%` 
                            }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>

            {/* 时间分布 */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="bg-dark-300 rounded-xl p-6 border border-accent-blue/30"
            >
              <h3 className="text-lg font-semibold text-white mb-4">时间分布</h3>
              {renderTimeDistribution(reportData.overall_analysis)}
              <div className="flex justify-between mt-4 text-xs text-gray-400">
                <span>00:00</span>
                <span>06:00</span>
                <span>12:00</span>
                <span>18:00</span>
                <span>23:59</span>
              </div>
            </motion.div>
          </div>
        )}

        {/* 智能体分析 */}
        {reportData && reportData.agent_analyses.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-dark-200 rounded-xl p-6 border border-accent-blue/20 shadow-lg"
          >
            <h3 className="text-xl font-semibold text-white mb-4">智能体分析</h3>
            <div className="bg-dark-300 rounded-lg overflow-hidden">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 px-4 py-3 border-b border-dark-400 text-sm font-medium text-gray-400">
                <div>智能体</div>
                <div>请求数</div>
                <div>风险分数</div>
                <div>风险等级</div>
                <div>建议</div>
              </div>
              {reportData.agent_analyses.map((agent) => (
                <div key={agent.agent_id} className="grid grid-cols-1 md:grid-cols-5 gap-4 px-4 py-3 border-b border-dark-400 items-center">
                  <div className="text-white font-medium">{agent.agent_name}</div>
                  <div className="text-gray-300">{agent.analysis.traffic_analysis.total_requests}</div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-dark-400 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${getRiskLevelColor(agent.analysis.summary.risk_level)}`}
                        style={{ width: `${Math.min(agent.analysis.summary.risk_score, 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-white">{agent.analysis.summary.risk_score.toFixed(1)}</span>
                  </div>
                  <div>
                    <span className={`px-2 py-1 rounded-full text-xs ${getRiskLevelColor(agent.analysis.summary.risk_level)}`}>
                      {agent.analysis.summary.risk_level === 'high' ? '高' : agent.analysis.summary.risk_level === 'medium' ? '中' : '低'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-400">
                    {agent.analysis.summary.recommendations[0] || '无'}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* 异常检测 */}
        {reportData && reportData.overall_analysis.anomalies.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="bg-dark-200 rounded-xl p-6 border border-accent-blue/20 shadow-lg"
          >
            <h3 className="text-xl font-semibold text-white mb-4">异常检测</h3>
            <div className="space-y-3">
              {reportData.overall_analysis.anomalies.map((anomaly, index) => (
                <div key={index} className="bg-dark-300 rounded-lg p-4 border-l-4 border-neon-pink">
                  <div className="flex justify-between items-start">
                    <div className="text-white font-medium">{anomaly.message}</div>
                    <div className="text-xs text-gray-400">{anomaly.request_time || ''}</div>
                  </div>
                  {anomaly.request_url && (
                    <div className="text-gray-300 text-sm mt-1">{anomaly.request_url}</div>
                  )}
                  <div className="mt-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${anomaly.severity === 'high' ? 'bg-red-900/30 text-red-400' : anomaly.severity === 'medium' ? 'bg-yellow-900/30 text-yellow-400' : 'bg-blue-900/30 text-blue-400'}`}>
                      {anomaly.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* 报告摘要 */}
        {reportData && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="bg-dark-200 rounded-xl p-6 border border-accent-blue/20 shadow-lg"
          >
            <h3 className="text-xl font-semibold text-white mb-4">报告摘要</h3>
            <div className="bg-dark-300 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <div className="text-gray-400 text-sm mb-1">报告时间</div>
                  <div className="text-white">{new Date(reportData.report_time).toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-gray-400 text-sm mb-1">时间窗口</div>
                  <div className="text-white">
                    {timeWindow === 'hour' ? '近1小时' : timeWindow === 'day' ? '近1天' : '近1周'}
                  </div>
                </div>
              </div>
              <div className="mb-4">
                <div className="text-gray-400 text-sm mb-2">风险等级分布</div>
                <div className="flex gap-4">
                  {Object.entries(reportData.summary.risk_level_distribution).map(([level, count]) => (
                    <div key={level} className="flex flex-col items-center">
                      <div className={`w-16 h-16 rounded-full flex items-center justify-center ${getRiskLevelColor(level)}`}>
                        {count}
                      </div>
                      <div className="mt-2 text-sm text-gray-300">
                        {level === 'high' ? '高' : level === 'medium' ? '中' : '低'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-gray-400 text-sm mb-2">改进建议</div>
                <ul className="space-y-2">
                  {reportData.summary.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <svg className="w-5 h-5 text-accent-blue mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-gray-300">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

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

export default NetworkAnalytics;