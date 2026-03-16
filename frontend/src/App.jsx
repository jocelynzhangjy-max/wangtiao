import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

// 导入页面组件
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import Tools from './pages/Tools';
import Chat from './pages/Chat';
import Settings from './pages/Settings';

// 导入组件
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Particles from './components/Particles';

// 导入状态管理
import useAuthStore from './stores/authStore';

function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [loading, setLoading] = useState(true);
  const { isAuthenticated, checkAuth, logout } = useAuthStore();

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        await checkAuth();
        setCurrentPage('dashboard');
      } catch (error) {
        setCurrentPage('login');
      } finally {
        setLoading(false);
      }
    };

    checkAuthentication();
  }, [checkAuth]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animated-background"></div>
        <div className="nebula-texture"></div>
        <motion.div
          className="w-16 h-16 border-4 border-accent-blue border-t-transparent rounded-full loading-spinner relative z-10"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
      </div>
    );
  }

  const renderPage = () => {
    if (!isAuthenticated) {
      if (currentPage === 'register') {
        return <Register onLogin={() => setCurrentPage('login')} />;
      }
      return <Login onRegister={() => setCurrentPage('register')} />;
    }

    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'agents':
        return <Agents />;
      case 'tools':
        return <Tools />;
      case 'chat':
        return <Chat />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen relative">
      <div className="animated-background"></div>
      <div className="nebula-texture"></div>
      
      {isAuthenticated ? (
        <>
          <Particles count={30} />
          <Navbar 
            title="AI Agent Gateway" 
            onLogout={logout}
            onPageChange={setCurrentPage}
          />
          <div className="flex relative z-10">
            <Sidebar onPageChange={setCurrentPage} currentPage={currentPage} />
            <main className="flex-1 p-6">
              {renderPage()}
            </main>
          </div>
        </>
      ) : (
        <div className="min-h-screen flex items-center justify-center p-4 relative z-10">
          <Particles count={50} />
          {renderPage()}
        </div>
      )}
    </div>
  );
}

export default App;