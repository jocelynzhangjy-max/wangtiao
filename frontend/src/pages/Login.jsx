import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import useAuthStore from '../stores/authStore';

const Login = ({ onRegister, onLoginSuccess }) => {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [inputFocus, setInputFocus] = useState({ email: false, password: false });
  const { login } = useAuthStore();
  
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');
    
    try {
      await login(data.email, data.password);
      console.log('Login successful in component');
      // 登录成功，调用回调函数
      if (onLoginSuccess) {
        onLoginSuccess();
      }
    } catch (err) {
      console.error('Login component error:', err);
      const errorMessage = err.response?.data?.detail || err.message || '邮箱或密码无效';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // 注册字段并整合onChange
  const registerField = (name, options = {}) => {
    const registered = register(name, options);
    return {
      ...registered,
      onChange: (e) => {
        registered.onChange(e);
      }
    };
  };

  return (
    <div className="w-full max-w-md">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="login-card-gradient login-card-enter"
      >
        <div className="login-card-content">
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-light-white mb-2">
              {Array.from("欢迎回来").map((char, index) => (
                <span
                  key={index}
                  className="text-char"
                  style={{
                    animationDelay: `${index * 0.1}s`,
                  }}
                >
                  {char}
                </span>
              ))}
            </h2>
            <p className="text-light-purple slide-in-right" style={{ animationDelay: '0.8s' }}>
              登录到您的 AI Agent Gateway 账户
            </p>
          </div>
          
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-accent-pink/20 text-accent-pink p-4 rounded-lg mb-6 border border-accent-pink/30"
            >
              {error}
            </motion.div>
          )}
          
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="mb-6 relative">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                邮箱
              </label>
              <div className="relative">
                <input
                  type="email"
                  {...registerField('email', { required: '邮箱是必填项' })}
                  className="input-cool w-full px-4 py-3 rounded-lg"
                  placeholder="请输入您的邮箱"
                  onFocus={() => setInputFocus(prev => ({ ...prev, email: true }))}
                  onBlur={() => setInputFocus(prev => ({ ...prev, email: false }))}
                />
                <div className={`input-progress ${inputFocus.email ? 'active' : ''}`}></div>
              </div>
              {errors.email && (
                <p className="text-accent-pink text-sm mt-1">{errors.email.message}</p>
              )}
            </div>
            
            <div className="mb-6 relative">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                密码
              </label>
              <div className="relative">
                <input
                  type="password"
                  {...registerField('password', { required: '密码是必填项' })}
                  className="input-cool w-full px-4 py-3 rounded-lg"
                  placeholder="请输入您的密码"
                  onFocus={() => setInputFocus(prev => ({ ...prev, password: true }))}
                  onBlur={() => setInputFocus(prev => ({ ...prev, password: false }))}
                />
                <div className={`input-progress ${inputFocus.password ? 'active' : ''}`}></div>
              </div>
              {errors.password && (
                <p className="text-accent-pink text-sm mt-1">{errors.password.message}</p>
              )}
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-cool font-medium disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? '登录中...' : '登录'}
            </button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              还没有账户？ 
              <button
                onClick={onRegister}
                className="link-underline font-medium ml-1"
              >
                注册
              </button>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
