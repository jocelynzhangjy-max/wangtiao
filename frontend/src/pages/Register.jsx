import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import useAuthStore from '../stores/authStore';

const Register = ({ onLogin, onRegisterSuccess }) => {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [inputFocus, setInputFocus] = useState({
    username: false,
    email: false,
    password: false,
    confirmPassword: false
  });
  const { register: registerUser, login } = useAuthStore();
  
  const { register, handleSubmit, formState: { errors }, watch } = useForm();
  const password = watch('password');

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // 注册新用户
      const success = await registerUser({
        username: data.username,
        email: data.email,
        password: data.password
      });
      
      if (success) {
        setSuccess('账户创建成功！正在自动登录...');
        
        // 注册成功后自动登录
        try {
          await login(data.email, data.password);
          console.log('Auto login successful');
          // 登录成功，调用回调函数
          if (onRegisterSuccess) {
            onRegisterSuccess();
          }
        } catch (loginErr) {
          console.error('Auto login failed:', loginErr);
          // 自动登录失败，跳转到登录页面
          setTimeout(() => onLogin(), 2000);
        }
      }
    } catch (err) {
      console.error('Registration error:', err);
      const errorMessage = err.response?.data?.detail || '创建账户失败，请重试。';
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
              {Array.from("创建账户").map((char, index) => (
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
              立即加入 AI Agent Gateway
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
          
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-accent-blue/20 text-accent-blue p-4 rounded-lg mb-6 border border-accent-blue/30"
            >
              {success}
            </motion.div>
          )}
          
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="mb-6 relative">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                用户名
              </label>
              <div className="relative">
                <input
                  type="text"
                  {...registerField('username', { 
                    required: '用户名是必填项',
                    minLength: { value: 3, message: '用户名至少需要3个字符' }
                  })}
                  className="input-cool w-full px-4 py-3 rounded-lg"
                  placeholder="请输入您的用户名"
                  onFocus={() => setInputFocus(prev => ({ ...prev, username: true }))}
                  onBlur={() => setInputFocus(prev => ({ ...prev, username: false }))}
                />
                <div className={`input-progress ${inputFocus.username ? 'active' : ''}`}></div>
              </div>
              {errors.username && (
                <p className="text-accent-pink text-sm mt-1">{errors.username.message}</p>
              )}
            </div>
            
            <div className="mb-6 relative">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                邮箱
              </label>
              <div className="relative">
                <input
                  type="email"
                  {...registerField('email', { 
                    required: '邮箱是必填项',
                    pattern: { 
                      value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                      message: '邮箱格式不正确'
                    }
                  })}
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
                  {...registerField('password', { 
                    required: '密码是必填项',
                    minLength: { value: 6, message: '密码至少需要6个字符' }
                  })}
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
            
            <div className="mb-6 relative">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                确认密码
              </label>
              <div className="relative">
                <input
                  type="password"
                  {...registerField('confirmPassword', { 
                    required: '请确认您的密码',
                    validate: value => value === password || '两次输入的密码不一致'
                  })}
                  className="input-cool w-full px-4 py-3 rounded-lg"
                  placeholder="请确认您的密码"
                  onFocus={() => setInputFocus(prev => ({ ...prev, confirmPassword: true }))}
                  onBlur={() => setInputFocus(prev => ({ ...prev, confirmPassword: false }))}
                />
                <div className={`input-progress ${inputFocus.confirmPassword ? 'active' : ''}`}></div>
              </div>
              {errors.confirmPassword && (
                <p className="text-accent-pink text-sm mt-1">{errors.confirmPassword.message}</p>
              )}
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-cool font-medium disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? '创建中...' : '注册'}
            </button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              已有账户？ 
              <button
                onClick={onLogin}
                className="link-underline font-medium ml-1"
              >
                登录
              </button>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Register;
