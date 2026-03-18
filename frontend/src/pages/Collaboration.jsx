import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const Collaboration = () => {
  const [teams, setTeams] = useState([]);
  const [agents, setAgents] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [isCreatingTeam, setIsCreatingTeam] = useState(false);
  const [newTeam, setNewTeam] = useState({ name: '', description: '' });
  const [isAddingMember, setIsAddingMember] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 获取所有团队
  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/collaboration/teams', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setTeams(response.data);
    } catch (err) {
      setError('获取团队列表失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 获取所有智能体
  const fetchAgents = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/agents', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setAgents(response.data);
    } catch (err) {
      console.error('获取智能体列表失败', err);
    }
  };

  // 获取团队成员
  const fetchTeamMembers = async (teamId) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/collaboration/teams/${teamId}/members`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setTeamMembers(response.data);
    } catch (err) {
      console.error('获取团队成员失败', err);
    }
  };

  // 创建团队
  const handleCreateTeam = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await axios.post('http://localhost:8000/api/collaboration/teams', {
        name: newTeam.name,
        description: newTeam.description
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setTeams([...teams, response.data]);
      setNewTeam({ name: '', description: '' });
      setIsCreatingTeam(false);
    } catch (err) {
      setError('创建团队失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 添加团队成员
  const handleAddMember = async () => {
    if (!selectedTeam || !selectedAgentId) return;
    
    try {
      setLoading(true);
      await axios.post(`http://localhost:8000/api/collaboration/teams/${selectedTeam.team_id}/members`, {
        agent_id: selectedAgentId,
        role: 'member'
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      fetchTeamMembers(selectedTeam.team_id);
      setSelectedAgentId('');
      setIsAddingMember(false);
    } catch (err) {
      setError('添加成员失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 移除团队成员
  const handleRemoveMember = async (memberId) => {
    if (!selectedTeam) return;
    
    try {
      setLoading(true);
      await axios.delete(`http://localhost:8000/api/collaboration/teams/${selectedTeam.team_id}/members/${memberId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      fetchTeamMembers(selectedTeam.team_id);
    } catch (err) {
      setError('移除成员失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 选择团队
  const handleSelectTeam = (team) => {
    setSelectedTeam(team);
    fetchTeamMembers(team.team_id);
  };

  useEffect(() => {
    fetchTeams();
    fetchAgents();
  }, []);

  return (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-dark-200 rounded-xl p-6 border border-accent-blue/20 shadow-lg"
      >
        <h2 className="text-2xl font-bold text-accent-blue mb-4">智能体协作管理</h2>
        <p className="text-gray-300 mb-6">管理智能体团队，实现安全高效的协作</p>

        {/* 创建团队按钮 */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-white">团队列表</h3>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsCreatingTeam(true)}
            className="bg-accent-blue hover:bg-accent-blue/80 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" />
            </svg>
            创建团队
          </motion.button>
        </div>

        {/* 创建团队表单 */}
        <AnimatePresence>
          {isCreatingTeam && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-dark-300 rounded-lg p-4 mb-6 border border-accent-blue/30"
            >
              <h4 className="text-lg font-medium text-white mb-3">创建新团队</h4>
              <form onSubmit={handleCreateTeam} className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">团队名称</label>
                  <input
                    type="text"
                    value={newTeam.name}
                    onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
                    required
                    className="w-full px-4 py-2 bg-dark-400 border border-accent-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-accent-blue"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">团队描述</label>
                  <textarea
                    value={newTeam.description}
                    onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 bg-dark-400 border border-accent-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-accent-blue"
                  ></textarea>
                </div>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-accent-blue hover:bg-accent-blue/80 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {loading ? '创建中...' : '创建团队'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsCreatingTeam(false)}
                    className="px-4 py-2 bg-dark-400 hover:bg-dark-500 text-gray-300 rounded-lg transition-colors"
                  >
                    取消
                  </button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 团队列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {teams.map((team) => (
            <motion.div
              key={team.team_id}
              whileHover={{ y: -5 }}
              className={`rounded-xl p-4 border transition-all ${selectedTeam?.team_id === team.team_id ? 'border-accent-blue bg-dark-300' : 'border-dark-400 bg-dark-200 hover:border-accent-blue/50'}`}
              onClick={() => handleSelectTeam(team)}
            >
              <h4 className="text-lg font-semibold text-white mb-2">{team.name}</h4>
              <p className="text-gray-400 text-sm mb-3">{team.description || '无描述'}</p>
              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>创建于: {new Date(team.created_at).toLocaleDateString()}</span>
                <span>成员: {team.member_count || 0}</span>
              </div>
            </motion.div>
          ))}
          {teams.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-400">
              <p>暂无团队，点击上方按钮创建</p>
            </div>
          )}
        </div>
      </motion.div>

      {/* 团队详情 */}
      {selectedTeam && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-dark-200 rounded-xl p-6 border border-accent-blue/20 shadow-lg"
        >
          <h3 className="text-xl font-semibold text-white mb-4">{selectedTeam.name} - 团队详情</h3>
          
          {/* 团队成员列表 */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h4 className="text-lg font-medium text-gray-300">团队成员</h4>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsAddingMember(true)}
                className="bg-accent-blue hover:bg-accent-blue/80 text-white px-3 py-1 rounded-lg text-sm flex items-center gap-2 transition-colors"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" />
                </svg>
                添加成员
              </motion.button>
            </div>

            {/* 添加成员表单 */}
            <AnimatePresence>
              {isAddingMember && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-dark-300 rounded-lg p-4 mb-4 border border-accent-blue/30"
                >
                  <h5 className="text-sm font-medium text-white mb-2">选择智能体</h5>
                  <div className="space-y-3">
                    <select
                      value={selectedAgentId}
                      onChange={(e) => setSelectedAgentId(e.target.value)}
                      className="w-full px-4 py-2 bg-dark-400 border border-accent-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-accent-blue"
                    >
                      <option value="">-- 选择智能体 --</option>
                      {agents.map((agent) => (
                        <option key={agent.id} value={agent.id}>
                          {agent.name} ({agent.agent_type})
                        </option>
                      ))}
                    </select>
                    <div className="flex gap-3">
                      <button
                        onClick={handleAddMember}
                        disabled={loading || !selectedAgentId}
                        className="flex-1 bg-accent-blue hover:bg-accent-blue/80 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {loading ? '添加中...' : '添加成员'}
                      </button>
                      <button
                        onClick={() => setIsAddingMember(false)}
                        className="px-4 py-2 bg-dark-400 hover:bg-dark-500 text-gray-300 rounded-lg transition-colors"
                      >
                        取消
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* 成员列表 */}
            <div className="bg-dark-300 rounded-lg overflow-hidden">
              <div className="grid grid-cols-4 gap-4 px-4 py-3 border-b border-dark-400 text-sm font-medium text-gray-400">
                <div>智能体</div>
                <div>角色</div>
                <div>加入时间</div>
                <div>操作</div>
              </div>
              {teamMembers.length > 0 ? (
                teamMembers.map((member) => (
                  <div key={member.id} className="grid grid-cols-4 gap-4 px-4 py-3 border-b border-dark-400 items-center">
                    <div className="text-white">{member.agent_name}</div>
                    <div className="text-accent-blue">{member.role}</div>
                    <div className="text-gray-400 text-sm">{new Date(member.created_at).toLocaleDateString()}</div>
                    <div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveMember(member.id);
                        }}
                        className="text-neon-pink hover:text-neon-pink/80 text-sm transition-colors"
                      >
                        移除
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-4 py-8 text-center text-gray-400">
                  暂无成员
                </div>
              )}
            </div>
          </div>

          {/* 团队协作设置 */}
          <div>
            <h4 className="text-lg font-medium text-gray-300 mb-3">协作设置</h4>
            <div className="bg-dark-300 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">协作模式</label>
                  <div className="text-white">{selectedTeam.collaboration_policy?.mode || '标准'}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">安全级别</label>
                  <div className="text-white">{selectedTeam.collaboration_policy?.security_level || '中等'}</div>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-300 mb-1">允许的操作</label>
                  <div className="flex flex-wrap gap-2">
                    {(selectedTeam.collaboration_policy?.allowed_operations || ['data_sharing', 'task_assignment']).map((op) => (
                      <span key={op} className="px-3 py-1 bg-dark-400 text-accent-blue rounded-full text-sm">
                        {op.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
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

export default Collaboration;