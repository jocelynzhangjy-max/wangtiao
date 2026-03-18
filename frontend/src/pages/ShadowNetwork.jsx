import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const ShadowNetwork = () => {
  const [stats, setStats] = useState({
    agents: { total: 0, with_sandbox: 0 },
    policies: 0,
    active_alerts: 0,
    gateway: { total_requests: 0, blocked_requests: 0, block_rate: 0 }
  });
  const [alerts, setAlerts] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, alertsRes, logsRes] = await Promise.all([
        axios.get('/api/shadow/dashboard/stats'),
        axios.get('/api/shadow/alerts'),
        axios.get('/api/shadow/audit-logs?limit=20')
      ]);

      setStats(statsRes.data);
      setAlerts(alertsRes.data);
      setAuditLogs(logsRes.data);
    } catch (error) {
      console.error('Error fetching shadow network data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await axios.post(`/api/shadow/alerts/${alertId}/acknowledge`);
      fetchDashboardData();
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      await axios.post(`/api/shadow/alerts/${alertId}/resolve`);
      fetchDashboardData();
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  const getRiskLevelColor = (level) => {
    const colors = {
      low: 'text-green-400',
      medium: 'text-yellow-400',
      high: 'text-orange-400',
      critical: 'text-red-500'
    };
    return colors[level] || 'text-gray-400';
  };

  const getRiskLevelBg = (level) => {
    const colors = {
      low: 'bg-green-500/20 border-green-500/30',
      medium: 'bg-yellow-500/20 border-yellow-500/30',
      high: 'bg-orange-500/20 border-orange-500/30',
      critical: 'bg-red-500/20 border-red-500/30'
    };
    return colors[level] || 'bg-gray-500/20 border-gray-500/30';
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
      >
        <h1 className="text-3xl font-bold text-white">影子网络监控</h1>
        <p className="text-gray-400 mt-2">AI Agent 安全隔离与审计系统</p>
      </motion.div>

      {/* 统计卡片 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-6"
      >
        <div className="bg-primary-module rounded-xl shadow-lg p-6 card-hover tech-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">受保护Agent</p>
              <h3 className="text-3xl font-bold text-white mt-2">
                {stats.agents.with_sandbox}/{stats.agents.total}
              </h3>
            </div>
            <div className="w-12 h-12 bg-accent-blue/20 rounded-full flex items-center justify-center border border-accent-blue/30">
              <svg className="w-6 h-6 text-accent-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-primary-module rounded-xl shadow-lg p-6 card-hover tech-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">安全策略</p>
              <h3 className="text-3xl font-bold text-white mt-2">{stats.policies}</h3>
            </div>
            <div className="w-12 h-12 bg-accent-purple/20 rounded-full flex items-center justify-center border border-accent-purple/30">
              <svg className="w-6 h-6 text-accent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-primary-module rounded-xl shadow-lg p-6 card-hover tech-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">活动告警</p>
              <h3 className="text-3xl font-bold text-accent-pink mt-2">{stats.active_alerts}</h3>
            </div>
            <div className="w-12 h-12 bg-accent-pink/20 rounded-full flex items-center justify-center border border-accent-pink/30">
              <svg className="w-6 h-6 text-accent-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-primary-module rounded-xl shadow-lg p-6 card-hover tech-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">拦截率</p>
              <h3 className="text-3xl font-bold text-white mt-2">
                {(stats.gateway.block_rate * 100).toFixed(1)}%
              </h3>
            </div>
            <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center border border-green-500/30">
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            {stats.gateway.blocked_requests} / {stats.gateway.total_requests} 请求
          </p>
        </div>
      </motion.div>

      {/* 标签页 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="bg-primary-module rounded-xl shadow-lg border border-dark-300"
      >
        <div className="border-b border-dark-300">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: '概览' },
              { id: 'alerts', label: `告警 (${alerts.length})` },
              { id: 'logs', label: '审计日志' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-accent-blue text-accent-blue'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-white">系统状态</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-dark-400/50 rounded-lg p-4">
                  <h4 className="text-accent-blue font-medium mb-2">影子网络功能</h4>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-center">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                      沙箱隔离环境
                    </li>
                    <li className="flex items-center">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                      动态策略控制
                    </li>
                    <li className="flex items-center">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                      意图审计分析
                    </li>
                    <li className="flex items-center">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                      身份联动管理
                    </li>
                    <li className="flex items-center">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                      异常行为检测
                    </li>
                  </ul>
                </div>
                <div className="bg-dark-400/50 rounded-lg p-4">
                  <h4 className="text-accent-purple font-medium mb-2">最近活动</h4>
                  <div className="space-y-2 text-sm text-gray-300">
                    {auditLogs.slice(0, 5).map((log, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="truncate">{log.event}</span>
                        <span className={`text-xs ${getRiskLevelColor(log.risk_level)}`}>
                          {log.risk_level}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div className="space-y-4">
              {alerts.length === 0 ? (
                <p className="text-gray-400 text-center py-8">暂无告警</p>
              ) : (
                alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-4 rounded-lg border ${getRiskLevelBg(alert.severity)}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="text-white font-medium">{alert.title}</h4>
                          <span className={`text-xs px-2 py-1 rounded ${getRiskLevelBg(alert.severity)} ${getRiskLevelColor(alert.severity)}`}>
                            {alert.severity}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded bg-dark-400 text-gray-300`}>
                            {alert.status}
                          </span>
                        </div>
                        <p className="text-gray-300 text-sm mb-2">{alert.description}</p>
                        <p className="text-gray-400 text-xs">
                          {new Date(alert.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex space-x-2 ml-4">
                        {alert.status === 'open' && (
                          <button
                            onClick={() => handleAcknowledgeAlert(alert.id)}
                            className="px-3 py-1 bg-accent-blue/20 text-accent-blue rounded text-sm hover:bg-accent-blue/30 transition-colors"
                          >
                            确认
                          </button>
                        )}
                        {alert.status !== 'resolved' && (
                          <button
                            onClick={() => handleResolveAlert(alert.id)}
                            className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-sm hover:bg-green-500/30 transition-colors"
                          >
                            解决
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-400 uppercase bg-dark-400/50">
                  <tr>
                    <th className="px-4 py-3">时间</th>
                    <th className="px-4 py-3">类型</th>
                    <th className="px-4 py-3">事件</th>
                    <th className="px-4 py-3">风险等级</th>
                    <th className="px-4 py-3">详情</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="border-b border-dark-300 hover:bg-dark-400/30">
                      <td className="px-4 py-3 text-gray-300">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 bg-dark-400 rounded text-xs text-gray-300">
                          {log.log_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-white">{log.event}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs ${getRiskLevelColor(log.risk_level)}`}>
                          {log.risk_level}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-xs">
                        {log.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default ShadowNetwork;
