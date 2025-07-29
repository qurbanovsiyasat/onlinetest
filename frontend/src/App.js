import React, { useState, useEffect, createContext, useContext, useRef } from "react";
import "./App.css";
import axios from "axios";
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import { motion, AnimatePresence } from 'framer-motion';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Dark Mode Context
const DarkModeContext = createContext();

const DarkModeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    // Check local storage first, then system preference
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme !== null) {
      return JSON.parse(savedTheme);
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    // Apply dark class to document
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    
    // Save preference
    localStorage.setItem('darkMode', JSON.stringify(isDark));
  }, [isDark]);

  const toggleDarkMode = () => {
    setIsDark(!isDark);
  };

  return (
    <DarkModeContext.Provider value={{ isDark, toggleDarkMode }}>
      {children}
    </DarkModeContext.Provider>
  );
};

const useDarkMode = () => {
  const context = useContext(DarkModeContext);
  if (!context) {
    throw new Error('useDarkMode must be used within a DarkModeProvider');
  }
  return context;
};

// Scroll to Top Component
const ScrollToTop = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const toggleVisibility = () => {
      if (window.pageYOffset > 300) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener('scroll', toggleVisibility);
    return () => window.removeEventListener('scroll', toggleVisibility);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.button
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-50 bg-indigo-600 dark:bg-indigo-500 text-white p-3 rounded-full shadow-lg hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors animate-float"
          style={{ backdropFilter: 'blur(10px)' }}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        </motion.button>
      )}
    </AnimatePresence>
  );
};

// Page Transition Wrapper
const PageTransition = ({ children, className = "" }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

// Emoji Reaction Component
const EmojiReactions = ({ answerId, currentUser }) => {
  const [reactions, setReactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userReaction, setUserReaction] = useState(null);

  const emojis = [
    { emoji: '👍', type: '👍', label: 'Thumbs up' },
    { emoji: '❤️', type: '❤️', label: 'Love' },
    { emoji: '😂', type: '😂', label: 'Laugh' },
    { emoji: '🤔', type: '🤔', label: 'Thinking' },
    { emoji: '🎉', type: '🎉', label: 'Celebrate' }
  ];

  useEffect(() => {
    if (currentUser && answerId) {
      fetchReactions();
    }
  }, [answerId, currentUser]);

  const fetchReactions = async () => {
    try {
      const response = await apiCall(`/answers/${answerId}/reactions`);
      setReactions(response.data.reactions || []);
      setUserReaction(response.data.user_reaction);
    } catch (error) {
      console.error('Error fetching reactions:', error);
    }
  };

  const handleReaction = async (emojiType) => {
    if (!currentUser || loading) return;
    
    setLoading(true);
    try {
      if (userReaction === emojiType) {
        // Remove reaction if same emoji clicked
        await apiCall(`/answers/${answerId}/react`, { method: 'DELETE' });
        setUserReaction(null);
      } else {
        // Add new reaction
        await apiCall(`/answers/${answerId}/react`, {
          method: 'POST',
          data: { emoji: emojiType }
        });
        setUserReaction(emojiType);
      }
      await fetchReactions();
    } catch (error) {
      console.error('Error updating reaction:', error);
    } finally {
      setLoading(false);
    }
  };

  const getReactionCount = (emojiType) => {
    const reaction = reactions.find(r => r.emoji === emojiType);
    return reaction ? reaction.count : 0;
  };

  const isUserReacted = (emojiType) => {
    return userReaction === emojiType;
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-wrap gap-2 mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
    >
      {emojis.map(({ emoji, type, label }) => {
        const count = getReactionCount(type);
        const isReacted = isUserReacted(type);
        
        return (
          <motion.button
            key={type}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleReaction(type)}
            disabled={loading}
            className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm transition-all ${
              isReacted 
                ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 border-2 border-indigo-300 dark:border-indigo-600' 
                : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
            }`}
            title={label}
          >
            <span className="text-lg">{emoji}</span>
            {count > 0 && (
              <span className={`font-medium ${isReacted ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-600 dark:text-gray-400'}`}>
                {count}
              </span>
            )}
          </motion.button>
        );
      })}
    </motion.div>
  );
};

// Enhanced Admin Badge Component with Tooltip
const AdminBadge = ({ size = 'default', showTooltip = true, className = '' }) => {
  const [showTooltipState, setShowTooltipState] = useState(false);
  
  const sizeClasses = {
    small: 'text-xs px-2 py-0.5',
    default: 'text-xs px-2.5 py-1', 
    large: 'text-sm px-3 py-1.5'
  };
  
  const iconSizes = {
    small: 'text-xs',
    default: 'text-sm',
    large: 'text-base'
  };
  
  return (
    <div className="relative inline-block">
      <span
        className={`bg-gradient-to-r from-purple-600 to-pink-600 text-white ${sizeClasses[size]} rounded-full font-bold shadow-sm border border-purple-300 flex items-center gap-1 ${className}`}
        onMouseEnter={() => showTooltip && setShowTooltipState(true)}
        onMouseLeave={() => setShowTooltipState(false)}
      >
        <span className={iconSizes[size]}>🛡️</span>
        <span>Admin</span>
      </span>
      
      {/* Tooltip */}
      {showTooltip && showTooltipState && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded shadow-lg whitespace-nowrap z-50"
        >
          This user is a verified administrator
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
        </motion.div>
      )}
    </div>
  );
};

// Enhanced Admin Name Component
const AdminName = ({ name, role, className = '' }) => {
  const isAdmin = role === 'admin';
  
  return (
    <span className={`${isAdmin ? 'font-bold text-purple-700 dark:text-purple-400' : 'font-medium text-gray-900 dark:text-gray-100'} ${className}`}>
      {name}
    </span>
  );
};

// Enhanced Admin Post Container
const AdminPostContainer = ({ children, isAdmin, className = '' }) => {
  if (!isAdmin) {
    return <div className={className}>{children}</div>;
  }
  
  return (
    <div className={`relative ${className}`}>
      {/* Purple border and enhanced background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-2 border-purple-300 dark:border-purple-600 rounded-lg shadow-md"></div>
      
      {/* Optional crown icon in corner */}
      <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white text-xs shadow-sm">
        👑
      </div>
      
      {/* Content */}
      <div className="relative">{children}</div>
    </div>
  );
};

// Dark Mode Toggle Component
const DarkModeToggle = () => {
  const { isDark, toggleDarkMode } = useDarkMode();
  
  return (
    <motion.button
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      onClick={toggleDarkMode}
      className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <motion.div
        initial={false}
        animate={{ rotate: isDark ? 180 : 0 }}
        transition={{ duration: 0.3 }}
      >
        {isDark ? (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.464 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
          </svg>
        )}
      </motion.div>
    </motion.button>
  );
};

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await axios.get(`${API}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user: userData } = response.data;
      localStorage.setItem('token', access_token);
      setUser(userData);
      return { success: true, user: userData };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (name, email, password) => {
    try {
      await axios.post(`${API}/auth/register`, { name, email, password });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Math rendering helper
const renderMathContent = (text) => {
  if (typeof text !== 'string') return text;
  
  // Simple check for LaTeX expressions
  if (text.includes('$') || text.includes('\\(') || text.includes('\\[')) {
    return (
      <span 
        dangerouslySetInnerHTML={{ __html: text }}
        className="tex2jax_process"
      />
    );
  }
  return text;
};

// Image cropping component
function ImageCropModal({ imageSrc, onCropComplete, onClose }) {
  const [crop, setCrop] = useState({
    unit: '%',
    width: 90,
    height: 90,
    x: 5,
    y: 5
  });
  const [completedCrop, setCompletedCrop] = useState(null);
  const imgRef = useRef(null);
  const canvasRef = useRef(null);

  const handleCropComplete = () => {
    if (completedCrop && imgRef.current && canvasRef.current) {
      const image = imgRef.current;
      const canvas = canvasRef.current;
      const crop = completedCrop;

      const scaleX = image.naturalWidth / image.width;
      const scaleY = image.naturalHeight / image.height;
      const ctx = canvas.getContext('2d');
      const pixelRatio = window.devicePixelRatio;

      canvas.width = crop.width * pixelRatio * scaleX;
      canvas.height = crop.height * pixelRatio * scaleY;

      ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      ctx.imageSmoothingQuality = 'high';

      ctx.drawImage(
        image,
        crop.x * scaleX,
        crop.y * scaleY,
        crop.width * scaleX,
        crop.height * scaleY,
        0,
        0,
        crop.width * scaleX,
        crop.height * scaleY
      );

      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onload = () => {
            onCropComplete(reader.result);
          };
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.95);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-screen overflow-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Crop Image</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <ReactCrop
              crop={crop}
              onChange={(c) => setCrop(c)}
              onComplete={(c) => setCompletedCrop(c)}
              aspect={undefined}
              className="max-w-full"
            >
              <img
                ref={imgRef}
                src={imageSrc}
                alt="Crop preview"
                className="max-w-full h-auto"
                style={{ maxHeight: '400px' }}
              />
            </ReactCrop>
          </div>

          <div className="lg:w-64">
            <h4 className="font-semibold mb-2">Preview:</h4>
            <canvas
              ref={canvasRef}
              className="border rounded max-w-full"
              style={{ maxWidth: '200px', maxHeight: '200px' }}
            />
            
            <div className="mt-4 space-y-2">
              <div className="text-sm text-gray-600">
                <p>Width: {Math.round(crop.width)}%</p>
                <p>Height: {Math.round(crop.height)}%</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-4 pt-4 mt-4 border-t">
          <button
            onClick={handleCropComplete}
            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition duration-200"
          >
            ✂️ Apply Crop
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition duration-200"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

// API helper with auth
const apiCall = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers
  };

  return axios({
    url: `${API}${url}`,
    headers,
    ...options
  });
};

function App() {
  return (
    <DarkModeProvider>
      <AuthProvider>
        <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300">
          <AnimatePresence mode="wait">
            <MainApp />
          </AnimatePresence>
          <ScrollToTop />
        </div>
      </AuthProvider>
    </DarkModeProvider>
  );
}

function MainApp() {
  const { user, loading } = useAuth();
  const [currentView, setCurrentView] = useState('home');

  // Local MathJax initialization for self-hosted setup
  useEffect(() => {
    const initializeMathJax = async () => {
      try {
        // Check if MathJax is already loaded from window
        if (window.MathJax && window.MathJax.typesetPromise) {
          console.log('✅ MathJax already loaded from window object');
          return;
        }
        
        // Use a safer MathJax loading approach to prevent webpack conflicts
        const loadMathJax = () => {
          // Only load if not already loading
          if (window.mathJaxLoading) return;
          window.mathJaxLoading = true;
          
          // Set configuration before loading to prevent conflicts
          window.MathJax = {
            tex: {
              inlineMath: [['$', '$'], ['\\(', '\\)']],
              displayMath: [['$$', '$$'], ['\\[', '\\]']]
            },
            svg: { fontCache: 'global' },
            startup: {
              ready() {
                window.MathJax.startup.defaultReady();
                console.log('✅ MathJax initialized successfully');
                window.mathJaxLoading = false;
              }
            }
          };
          
          const script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js';
          script.async = true;
          script.onload = () => console.log('✅ MathJax loaded from CDN');
          script.onerror = () => {
            console.warn('⚠️ MathJax CDN loading failed');
            window.mathJaxLoading = false;
          };
          document.head.appendChild(script);
        };
        
        // Delay MathJax loading to avoid conflicts with React 18
        setTimeout(loadMathJax, 100);
        
      } catch (error) {
        console.warn('⚠️ MathJax initialization failed:', error);
      }
    };
    
    initializeMathJax();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  if (user.role === 'admin') {
    return <AdminDashboard currentView={currentView} setCurrentView={setCurrentView} />;
  }

  return <UserDashboard currentView={currentView} setCurrentView={setCurrentView} />;
}

// Authentication Screen
function AuthScreen() {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    let result;
    if (isLogin) {
      result = await login(formData.email, formData.password);
    } else {
      result = await register(formData.name, formData.email, formData.password);
      if (result.success) {
        setIsLogin(true);
        setError('Registration successful! Please log in.');
      }
    }

    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  const initializeAdmin = async () => {
    try {
      const response = await axios.post(`${API}/init-admin`);
      // Admin initialization successful - no alert needed
    } catch (error) {
      // Admin already exists or error occurred - no alert needed
    }
  };

  return (
    <PageTransition className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      {/* Dark Mode Toggle - Fixed position */}
      <div className="fixed top-4 right-4 z-50">
        <DarkModeToggle />
      </div>
      
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8"
      >
        <div className="text-center mb-8">
          <motion.h1 
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-3xl font-bold text-indigo-900 dark:text-indigo-400 mb-2"
          >
            📝 Squiz
          </motion.h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2">Ad və soyad</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full p-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                placeholder="Enter your full name"
                required
              />
            </motion.div>
          )}

          <div>
            <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 dark:text-gray-300 font-semibold mb-2">Şifrə</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`p-3 rounded-lg ${error.includes('successful') ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300' : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'}`}
            >
              {error}
            </motion.div>
          )}

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 dark:bg-indigo-500 text-white py-3 rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-600 transition duration-200 font-semibold disabled:opacity-50"
          >
            {loading ? 'Processing...' : (isLogin ? 'Giriş' : 'Qeydiyyat')}
          </motion.button>
        </form>

        <div className="mt-6 text-center">
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
              setFormData({ name: '', email: '', password: '' });
            }}
            className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-semibold transition-colors"
          >
            {isLogin ? "Yeni hesab yarat" : "Giriş yerinə qayıt"}
          </motion.button>
        </div>

        {/* Initialize admin automatically on backend if needed */}
      </motion.div>
    </PageTransition>
  );
}

// Admin Dashboard
function AdminDashboard({ currentView, setCurrentView }) {
  const { user, logout } = useAuth();
  const [users, setUsers] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [quizResults, setQuizResults] = useState([]);
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    if (currentView === 'users') fetchUsers();
    if (currentView === 'quizzes') fetchQuizzes();
    if (currentView === 'categories') fetchCategories();
    if (currentView === 'results') fetchQuizResults();
    if (currentView === 'dashboard') fetchAnalytics();
  }, [currentView]);

  const fetchUsers = async () => {
    try {
      const response = await apiCall('/admin/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchQuizzes = async () => {
    try {
      const response = await apiCall('/admin/quizzes');
      setQuizzes(response.data);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await apiCall('/admin/categories');
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchQuizResults = async () => {
    try {
      const response = await apiCall('/admin/quiz-results');
      setQuizResults(response.data);
    } catch (error) {
      console.error('Error fetching quiz results:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await apiCall('/admin/analytics/summary');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  return (
    <PageTransition className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <div className="mb-4 sm:mb-0">
            <h1 className="text-xl sm:text-2xl font-bold text-gray-800 dark:text-gray-200">👑 Admin Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">Xoş gəldiniz, {user.name}</p>
          </div>
          <div className="flex items-center gap-3">
            <DarkModeToggle />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={logout}
              className="bg-red-600 dark:bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-700 dark:hover:bg-red-600 transition duration-200 text-sm sm:text-base"
            >
              Çıxış
            </motion.button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-2 sm:px-4 py-4 sm:py-8">
        <div className="flex flex-wrap gap-2 sm:gap-4 mb-6 sm:mb-8 overflow-x-auto pb-2">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('dashboard')}
            className={`px-3 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
              currentView === 'dashboard' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            📊 İstifadəçi Paneli
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('users')}
            className={`px-3 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
              currentView === 'users' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            👥 Users
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('quizzes')}
            className={`px-3 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
              currentView === 'quizzes' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            📝 Sınaqlar
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('results')}
            className={`px-3 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
              currentView === 'results' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            📈 Results
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('categories')}
            className={`px-3 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
              currentView === 'categories' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            🗂️ Categories
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('qa-management')}
            className={`px-3 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
              currentView === 'qa-management' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            💬 Q&A Forum
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('profile')}
            className={`px-3 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
              currentView === 'profile' ? 'bg-purple-600 dark:bg-purple-500 text-white' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            👤 My Profile
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('create-quiz')}
            className={`px-3 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
              currentView === 'create-quiz' ? 'bg-green-600 dark:bg-green-500 text-white' : 'bg-green-600 dark:bg-green-500 text-white hover:bg-green-700 dark:hover:bg-green-600'
            }`}
          >
            ➕ Create Quiz
          </motion.button>
        </div>

        {/* Content */}
        {currentView === 'dashboard' && <AdminDashboardHome analytics={analytics} />}
        {currentView === 'users' && <AdminUsersView users={users} />}
        {currentView === 'quizzes' && <AdminQuizzesView quizzes={quizzes} fetchQuizzes={fetchQuizzes} />}
        {currentView === 'results' && <AdminResultsView results={quizResults} />}
        {currentView === 'categories' && <AdminCategoriesView categories={categories} fetchCategories={fetchCategories} />}
        {currentView === 'qa-management' && <AdminQAManagement />}
        {currentView === 'profile' && <UserProfile user={user} />}
        {currentView === 'create-quiz' && <AdminCreateQuiz setCurrentView={setCurrentView} />}
      </div>
    </PageTransition>
  );
}

// Admin Dashboard Components
function AdminDashboardHome({ analytics }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
        >
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400">
              👥
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Users</h3>
              <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{analytics.total_users || 0}</p>
            </div>
          </div>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
        >
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400">
              📝
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Quizzes</h3>
              <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{analytics.total_quizzes || 0}</p>
            </div>
          </div>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
        >
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-400">
              📊
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Attempts</h3>
              <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{analytics.total_attempts || 0}</p>
            </div>
          </div>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
        >
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-400">
              🎯
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Average Score</h3>
              <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{analytics.average_score || 0}%</p>
            </div>
          </div>
        </motion.div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
        >
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">📈 Platform Overview</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Most Popular Quiz:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">{analytics.most_popular_quiz || 'None'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Platform Status:</span>
              <span className="text-green-600 dark:text-green-400 font-medium">Active</span>
            </div>
          </div>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
        >
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">🚀 Quick Actions</h3>
          <div className="space-y-2">
            <p className="text-gray-600 dark:text-gray-400">• Create new quizzes and manage content</p>
            <p className="text-gray-600 dark:text-gray-400">• View detailed user test results</p>
            <p className="text-gray-600 dark:text-gray-400">• Manage user accounts and permissions</p>
            <p className="text-gray-600 dark:text-gray-400">• Organize quizzes by categories</p>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}

function AdminResultsView({ results }) {
  const [filterBy, setFilterBy] = useState('all');
  const [sortBy, setSortBy] = useState('date_desc');
  
  // Filter and sort results
  const filteredAndSortedResults = results
    .filter(result => {
      if (filterBy === 'all') return true;
      if (filterBy === 'high_score') return result.percentage >= 80;
      if (filterBy === 'low_score') return result.percentage < 60;
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date_desc':
          return new Date(b.attempted_at) - new Date(a.attempted_at);
        case 'date_asc':
          return new Date(a.attempted_at) - new Date(b.attempted_at);
        case 'score_desc':
          return b.percentage - a.percentage;
        case 'score_asc':
          return a.percentage - b.percentage;
        case 'user_name':
          return a.user.name.localeCompare(b.user.name);
        default:
          return 0;
      }
    });

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600 bg-green-100';
    if (percentage >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreBadge = (percentage) => {
    if (percentage >= 80) return 'Əla';
    if (percentage >= 60) return 'Yaxşı';
    return 'Təkmilləşdirməyə ehtiyac var';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">📈 User Test Results</h2>
        <div className="flex gap-4">
          <select
            value={filterBy}
            onChange={(e) => setFilterBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Results</option>
            <option value="high_score">High Scores (80%+)</option>
            <option value="low_score">Low Scores (&lt;60%)</option>
          </select>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="date_desc">Newest First</option>
            <option value="date_asc">Oldest First</option>
            <option value="score_desc">Highest Score</option>
            <option value="score_asc">Lowest Score</option>
            <option value="user_name">User Name</option>
          </select>
        </div>
      </div>

      {filteredAndSortedResults.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No test results found.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left py-3 px-4 font-medium text-gray-700">User</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Quiz</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Category</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Score</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Percentage</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Performance</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedResults.map((result, index) => (
                <tr key={index} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div>
                      <p className="font-semibold text-gray-800">{result.user.name}</p>
                      <p className="text-sm text-gray-500">{result.user.email}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <p className="font-medium text-gray-800">{result.quiz.title}</p>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-block px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded">
                      {result.quiz.category}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <p className="font-semibold">{result.score}/{result.total_questions}</p>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-1 rounded text-sm font-semibold ${getScoreColor(result.percentage)}`}>
                      {result.percentage.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getScoreColor(result.percentage)}`}>
                      {getScoreBadge(result.percentage)}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <p className="text-sm text-gray-600">
                      {new Date(result.attempted_at).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date(result.attempted_at).toLocaleTimeString()}
                    </p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold text-gray-800 mb-2">📊 Ümumi Statistikalar</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Ümumi Nəticələr:</p>
            <p className="font-semibold">{filteredAndSortedResults.length}</p>
          </div>
          <div>
            <p className="text-gray-600">Yüksək Nəticə (80%+):</p>
            <p className="font-semibold text-green-600">
              {filteredAndSortedResults.filter(r => r.percentage >= 80).length}
            </p>
          </div>
          <div>
            <p className="text-gray-600">Average Score:</p>
            <p className="font-semibold">
              {filteredAndSortedResults.length > 0 
                ? (filteredAndSortedResults.reduce((sum, r) => sum + r.percentage, 0) / filteredAndSortedResults.length).toFixed(1)
                : 0}%
            </p>
          </div>
          <div>
            <p className="text-gray-600">Low Scores (&lt;60%):</p>
            <p className="font-semibold text-red-600">
              {filteredAndSortedResults.filter(r => r.percentage < 60).length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function AdminUsersView({ users }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Registered Users</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Name</th>
              <th className="text-left py-2">Email</th>
              <th className="text-left py-2">Role</th>
              <th className="text-left py-2">Status</th>
              <th className="text-left py-2">Joined</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b">
                <td className="py-2">{user.name}</td>
                <td className="py-2">{user.email}</td>
                <td className="py-2">
                  <span className={`px-2 py-1 rounded text-xs ${user.role === 'admin' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'}`}>
                    {user.role}
                  </span>
                </td>
                <td className="py-2">
                  <span className={`px-2 py-1 rounded text-xs ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="py-2">{new Date(user.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AdminQuizzesView({ quizzes, fetchQuizzes }) {
  const [editingQuiz, setEditingQuiz] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [subjectsStructure, setSubjectsStructure] = useState({});
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'folders'
  const [movingQuiz, setMovingQuiz] = useState(null);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [moveDestination, setMoveDestination] = useState({ subject: '', subcategory: 'General' });
  const [predefinedSubjects, setPredefinedSubjects] = useState({});
  
  // Bulk publish state
  const [selectedQuizzes, setSelectedQuizzes] = useState(new Set());
  const [showBulkPublishModal, setShowBulkPublishModal] = useState(false);
  const [bulkPublishingQuizzes, setBulkPublishingQuizzes] = useState(false);

  useEffect(() => {
    if (viewMode === 'folders') {
      fetchSubjectsStructure();
    }
    fetchPredefinedSubjects();
  }, [viewMode]);

  const fetchSubjectsStructure = async () => {
    try {
      const response = await apiCall('/admin/subjects-structure');
      setSubjectsStructure(response.data);
    } catch (error) {
      console.error('Error fetching subjects structure:', error);
    }
  };

  const fetchPredefinedSubjects = async () => {
    try {
      const response = await apiCall('/admin/predefined-subjects');
      setPredefinedSubjects(response.data);
    } catch (error) {
      console.error('Error fetching subjects:', error);
    }
  };

  const [deleteConfirmation, setDeleteConfirmation] = useState({ show: false, quizId: null, quizTitle: '' });

  const deleteQuiz = async (quizId, quizTitle = 'this quiz') => {
    setDeleteConfirmation({ show: true, quizId, quizTitle });
  };

  const confirmDeleteQuiz = async () => {
    const { quizId } = deleteConfirmation;
    try {
      console.log('Attempting to delete quiz with ID:', quizId);
      const response = await apiCall(`/admin/quiz/${quizId}`, { method: 'DELETE' });
      console.log('Delete response:', response);
      
      // Show success message
      alert('Quiz deleted successfully!');
      
      // Refresh quiz list
      fetchQuizzes();
      if (viewMode === 'folders') {
        fetchSubjectsStructure();
      }
      
      setDeleteConfirmation({ show: false, quizId: null, quizTitle: '' });
    } catch (error) {
      console.error('Error deleting quiz:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';
      alert(`Error deleting quiz: ${errorMessage}`);
      setDeleteConfirmation({ show: false, quizId: null, quizTitle: '' });
    }
  };

  const editQuiz = async (quiz) => {
    try {
      // Get detailed quiz information for editing
      const response = await apiCall(`/admin/quiz/${quiz.id}/edit-details`);
      setEditingQuiz(response.data.quiz);
      setShowEditModal(true);
    } catch (error) {
      alert('Error loading quiz details: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const updateQuiz = async (quizId, updateData) => {
    try {
      await apiCall(`/admin/quiz/${quizId}`, {
        method: 'PUT',
        data: updateData
      });
      setShowEditModal(false);
      setEditingQuiz(null);
      fetchQuizzes();
      if (viewMode === 'folders') {
        fetchSubjectsStructure();
      }
      alert('Quiz updated successfully!');
    } catch (error) {
      alert('Error updating quiz: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const toggleQuizVisibility = async (quiz) => {
    try {
      await apiCall(`/admin/quiz/${quiz.id}`, {
        method: 'PUT',
        data: { is_public: !quiz.is_public }
      });
      fetchQuizzes();
      if (viewMode === 'folders') {
        fetchSubjectsStructure();
      }
    } catch (error) {
      alert('Error updating quiz visibility');
    }
  };

  const toggleQuizPublish = async (quiz) => {
    try {
      if (quiz.is_draft) {
        // Publish the quiz
        await apiCall(`/admin/quiz/${quiz.id}/publish`, {
          method: 'POST'
        });
        alert('Quiz published successfully! Users can now take this quiz.');
      } else {
        // Cannot unpublish - would need a separate endpoint for that
        alert('Quiz is already published. To make changes, please create a new version.');
        return;
      }
      fetchQuizzes();
      if (viewMode === 'folders') {
        fetchSubjectsStructure();
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
      alert('Error publishing quiz: ' + errorMessage);
    }
  };

  const moveQuiz = (quiz) => {
    setMovingQuiz(quiz);
    setMoveDestination({ 
      subject: quiz.subject || Object.keys(predefinedSubjects)[0] || '', 
      subcategory: quiz.subcategory || 'General' 
    });
    setShowMoveModal(true);
  };

  const handleMoveQuiz = async () => {
    if (!movingQuiz || !moveDestination.subject) {
      alert('Please select a destination folder');
      return;
    }

    try {
      await apiCall(`/admin/quiz/${movingQuiz.id}/move-folder`, {
        method: 'POST',
        data: {
          new_subject: moveDestination.subject,
          new_subcategory: moveDestination.subcategory
        }
      });

      setShowMoveModal(false);
      setMovingQuiz(null);
      fetchQuizzes();
      if (viewMode === 'folders') {
        fetchSubjectsStructure();
      }
      alert('Quiz moved successfully!');
    } catch (error) {
      alert('Error moving quiz: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const getSubcategoriesForMove = () => {
    return predefinedSubjects[moveDestination.subject] || ['General'];
  };

  // Bulk publish functionality
  const handleBulkPublish = async () => {
    setBulkPublishingQuizzes(true);
    let successCount = 0;
    let errorCount = 0;
    const errors = [];

    try {
      for (const quizId of selectedQuizzes) {
        try {
          await apiCall(`/admin/quiz/${quizId}/publish`, {
            method: 'POST'
          });
          successCount++;
        } catch (error) {
          errorCount++;
          errors.push(`Quiz ${quizId}: ${error.response?.data?.detail || 'Unknown error'}`);
        }
      }

      if (successCount > 0) {
        alert(`✅ Successfully published ${successCount} quiz${successCount > 1 ? 'es' : ''}!`);
      }
      if (errorCount > 0) {
        alert(`⚠️ Failed to publish ${errorCount} quiz${errorCount > 1 ? 'es' : ''}:\n${errors.join('\n')}`);
      }

      // Refresh the quiz list and clear selection
      await fetchQuizzes();
      setSelectedQuizzes(new Set());
      setShowBulkPublishModal(false);
    } catch (error) {
      alert('Error during bulk publish: ' + (error.message || 'Unknown error'));
    } finally {
      setBulkPublishingQuizzes(false);
    }
  };

  const getDraftQuizzesCount = () => {
    return quizzes.filter(q => q.is_draft).length;
  };

  const getSelectedDraftQuizzes = () => {
    return quizzes.filter(q => selectedQuizzes.has(q.id) && q.is_draft);
  };

  const QuizCard = ({ quiz, showSubject = true }) => {
    const isSelected = selectedQuizzes.has(quiz.id);
    const isDraft = quiz.is_draft;
    
    const handleSelectChange = (e) => {
      const newSelection = new Set(selectedQuizzes);
      if (e.target.checked) {
        newSelection.add(quiz.id);
      } else {
        newSelection.delete(quiz.id);
      }
      setSelectedQuizzes(newSelection);
    };
    
    return (
      <div className="border rounded-lg p-4 relative">
        {/* Selection checkbox - only for draft quizzes */}
        {isDraft && (
          <div className="absolute top-2 right-2 z-10">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={handleSelectChange}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
          </div>
        )}
        
        <div className="mb-2 flex flex-wrap gap-1">
          <span className={`inline-block px-2 py-1 rounded text-xs ${
            quiz.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {quiz.is_public ? 'Public' : 'Private'}
          </span>
          <span className={`inline-block px-2 py-1 rounded text-xs ${
            quiz.is_draft ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {quiz.is_draft ? '📝 Draft' : '✅ Published'}
          </span>
          {showSubject && (
            <>
              <span className="inline-block px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                {quiz.subject || 'General'}
              </span>
              <span className="inline-block px-2 py-1 rounded text-xs bg-purple-100 text-purple-800">
                {quiz.subcategory || 'General'}
              </span>
            </>
          )}
        </div>
      
      {quiz.is_draft && (
        <div className="mb-3 p-2 bg-orange-50 border-l-4 border-orange-400 rounded">
          <p className="text-xs text-orange-700">
            ⚠️ This quiz is in draft mode. Users cannot take it until published.
          </p>
        </div>
      )}
      
      <h3 className="font-semibold text-gray-800 mb-2">{quiz.title}</h3>
      <p className="text-gray-600 text-sm mb-2 line-clamp-2">{quiz.description}</p>
      
      <div className="flex justify-between items-center text-sm text-gray-500 mb-3">
        <span>{quiz.category}</span>
        <span>{quiz.total_questions} questions</span>
      </div>

      <div className="flex justify-between items-center text-sm text-gray-500 mb-3">
        <span>{quiz.total_attempts || 0} attempts</span>
        <span className="font-medium">
          Avg: {quiz.average_score || 0}%
        </span>
      </div>
      
      <div className="text-xs text-gray-400 mb-3">
        Created: {new Date(quiz.created_at).toLocaleDateString()}
        {quiz.updated_at !== quiz.created_at && (
          <div>Updated: {new Date(quiz.updated_at).toLocaleDateString()}</div>
        )}
      </div>
      
      <div className="grid grid-cols-2 gap-1 text-xs mb-2">
        <button
          onClick={() => editQuiz(quiz)}
          className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition duration-200"
        >
          ✏️ Edit
        </button>
        <button
          onClick={() => toggleQuizPublish(quiz)}
          className={`py-2 rounded transition duration-200 ${
            quiz.is_draft 
              ? 'bg-green-600 text-white hover:bg-green-700' 
              : 'bg-gray-400 text-white cursor-not-allowed'
          }`}
          disabled={!quiz.is_draft}
        >
          {quiz.is_draft ? '🚀 Publish' : '✅ Published'}
        </button>
      </div>
      
      <div className="grid grid-cols-2 gap-1 text-xs mb-2">
        <button
          onClick={() => toggleQuizVisibility(quiz)}
          className={`py-2 rounded transition duration-200 ${
            quiz.is_public 
              ? 'bg-yellow-600 text-white hover:bg-yellow-700' 
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
        >
          {quiz.is_public ? '🔒 Private' : '🔓 Public'}
        </button>
        <button
          onClick={() => moveQuiz(quiz)}
          className="bg-purple-600 text-white py-2 rounded hover:bg-purple-700 transition duration-200"
        >
          📁 Move
        </button>
      </div>
      
      <div className="grid grid-cols-1 gap-1 text-xs">
        <button
          onClick={() => deleteQuiz(quiz.id, quiz.title)}
          className="bg-red-600 text-white py-2 rounded hover:bg-red-700 transition duration-200"
        >
          🗑️ Delete
        </button>
      </div>
    </div>
    );
  };

  const ListView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {quizzes.map((quiz) => (
        <QuizCard key={quiz.id} quiz={quiz} />
      ))}
    </div>
  );

  const FoldersView = () => (
    <div className="space-y-6">
      {Object.entries(subjectsStructure).map(([subjectName, subjectData]) => (
        <div key={subjectName} className="bg-gray-50 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-800">
              📁 {subjectName}
            </h3>
            <span className="ml-3 px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
              {subjectData.total_quizzes} quizzes
            </span>
          </div>

          <div className="space-y-4">
            {Object.entries(subjectData.subcategories).map(([subcategoryName, subcategoryData]) => (
              <div key={subcategoryName} className="bg-white rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <h4 className="text-lg font-medium text-gray-700">
                    📂 {subcategoryName}
                  </h4>
                  <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                    {subcategoryData.quiz_count} quizzes
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {subcategoryData.quizzes.map((quiz) => (
                    <QuizCard key={quiz.id} quiz={quiz} showSubject={false} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">
          Quiz Management (Sorted by Date)
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('list')}
            className={`px-4 py-2 rounded-lg transition duration-200 ${
              viewMode === 'list' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📋 List View
          </button>
          <button
            onClick={() => setViewMode('folders')}
            className={`px-4 py-2 rounded-lg transition duration-200 ${
              viewMode === 'folders' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📁 Folder View
          </button>
        </div>
      </div>
      
      {/* Bulk Actions Bar */}
      {selectedQuizzes.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-blue-800">
                {selectedQuizzes.size} quiz{selectedQuizzes.size > 1 ? 'es' : ''} selected
              </span>
              <button
                onClick={() => setSelectedQuizzes(new Set())}
                className="text-blue-600 hover:text-blue-800 text-sm underline"
              >
                Clear selection
              </button>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowBulkPublishModal(true)}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition duration-200"
                disabled={bulkPublishingQuizzes}
              >
                {bulkPublishingQuizzes ? '⏳ Publishing...' : '🚀 Bulk Publish'}
              </button>
            </div>
          </div>
        </div>
      )}

      {viewMode === 'list' ? <ListView /> : <FoldersView />}

      {/* Edit Quiz Modal */}
      {showEditModal && editingQuiz && (
        <QuizEditModal
          quiz={editingQuiz}
          onClose={() => {
            setShowEditModal(false);
            setEditingQuiz(null);
          }}
          onUpdate={updateQuiz}
        />
      )}

      {/* Delete Quiz Confirmation Modal */}
      {deleteConfirmation.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">🗑️</div>
              <h3 className="text-lg font-semibold mb-2">Delete Quiz?</h3>
              <p className="text-gray-600 text-sm">
                Are you sure you want to delete "{deleteConfirmation.quizTitle}"?
              </p>
              <p className="text-red-600 text-sm mt-2">
                ⚠️ This action cannot be undone.
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={confirmDeleteQuiz}
                className="flex-1 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition duration-200 font-semibold"
              >
                Yes, Delete
              </button>
              <button
                onClick={() => setDeleteConfirmation({ show: false, quizId: null, quizTitle: '' })}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Move Quiz Modal */}
      {showMoveModal && movingQuiz && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold">Move Quiz to Different Folder</h3>
              <button
                onClick={() => {
                  setShowMoveModal(false);
                  setMovingQuiz(null);
                }}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ✕
              </button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-3">
                Moving quiz: <strong>"{movingQuiz.title}"</strong>
              </p>
              <p className="text-xs text-gray-500 mb-4">
                Current location: {movingQuiz.subject || 'General'} → {movingQuiz.subcategory || 'General'}
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 font-semibold mb-2">Destination Subject *</label>
                <select
                  value={moveDestination.subject}
                  onChange={(e) => setMoveDestination({ 
                    ...moveDestination, 
                    subject: e.target.value, 
                    subcategory: 'General' 
                  })}
                  className="w-full p-3 border border-gray-300 rounded-lg"
                >
                  {Object.keys(predefinedSubjects).map(subject => (
                    <option key={subject} value={subject}>{subject}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Destination Subcategory</label>
                <select
                  value={moveDestination.subcategory}
                  onChange={(e) => setMoveDestination({ 
                    ...moveDestination, 
                    subcategory: e.target.value 
                  })}
                  className="w-full p-3 border border-gray-300 rounded-lg"
                >
                  {getSubcategoriesForMove().map(subcategory => (
                    <option key={subcategory} value={subcategory}>{subcategory}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-4 pt-6">
              <button
                onClick={handleMoveQuiz}
                className="flex-1 bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition duration-200 font-semibold"
              >
                📁 Move Quiz
              </button>
              <button
                onClick={() => {
                  setShowMoveModal(false);
                  setMovingQuiz(null);
                }}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Publish Modal */}
      {showBulkPublishModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">🚀</div>
              <h3 className="text-lg font-semibold mb-2">Bulk Publish Quizzes</h3>
              <p className="text-gray-600 text-sm">
                Are you sure you want to publish {selectedQuizzes.size} selected quiz{selectedQuizzes.size > 1 ? 'es' : ''}?
              </p>
              <p className="text-blue-600 text-sm mt-2">
                ✅ Published quizzes will be available for users to take immediately.
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg mb-4">
              <p className="text-sm text-gray-700 font-medium mb-2">Selected Quizzes:</p>
              <div className="max-h-32 overflow-y-auto">
                {getSelectedDraftQuizzes().map(quiz => (
                  <div key={quiz.id} className="text-xs text-gray-600 py-1 border-b border-gray-200">
                    📝 {quiz.title}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleBulkPublish}
                disabled={bulkPublishingQuizzes}
                className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold disabled:opacity-50"
              >
                {bulkPublishingQuizzes ? '⏳ Publishing...' : '🚀 Publish All'}
              </button>
              <button
                onClick={() => setShowBulkPublishModal(false)}
                disabled={bulkPublishingQuizzes}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function QuizEditModal({ quiz, onClose, onUpdate }) {
  const [editData, setEditData] = useState({
    title: quiz.title,
    description: quiz.description,
    category: quiz.category,
    subject: quiz.subject || '',
    subcategory: quiz.subcategory || 'General',
    is_public: quiz.is_public,
    is_active: quiz.is_active,
    allowed_users: quiz.allowed_users || [],
    questions: [...quiz.questions] // Deep copy of questions
  });

  const [predefinedSubjects, setPredefinedSubjects] = useState({});
  const [allUsers, setAllUsers] = useState([]);
  const [editingQuestionIndex, setEditingQuestionIndex] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);

  useEffect(() => {
    fetchPredefinedSubjects();
    if (editData.is_public) {
      fetchAllUsers();
    }
  }, [editData.is_public]);

  const fetchPredefinedSubjects = async () => {
    try {
      const response = await apiCall('/admin/predefined-subjects');
      setPredefinedSubjects(response.data);
    } catch (error) {
      console.error('Error fetching subjects:', error);
    }
  };

  const fetchAllUsers = async () => {
    try {
      const response = await apiCall('/admin/users');
      setAllUsers(response.data.filter(user => user.role === 'user'));
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setUploadingImage(true);
      const response = await apiCall('/admin/upload-image', {
        method: 'POST',
        data: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      return response.data.url;
    } catch (error) {
      alert('Error uploading image: ' + (error.response?.data?.detail || 'Unknown error'));
      return null;
    } finally {
      setUploadingImage(false);
    }
  };

  const handleImageUpload = async (event, questionIndex) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    const imageUrl = await uploadImage(file);
    if (imageUrl) {
      const updatedQuestions = [...editData.questions];
      updatedQuestions[questionIndex].image_url = imageUrl;
      setEditData({ ...editData, questions: updatedQuestions });
    }
  };

  const removeImage = (questionIndex) => {
    const updatedQuestions = [...editData.questions];
    updatedQuestions[questionIndex].image_url = null;
    setEditData({ ...editData, questions: updatedQuestions });
  };

  const updateQuestion = (questionIndex, field, value) => {
    const updatedQuestions = [...editData.questions];
    updatedQuestions[questionIndex][field] = value;
    setEditData({ ...editData, questions: updatedQuestions });
  };

  const updateQuestionOption = (questionIndex, optionIndex, field, value) => {
    const updatedQuestions = [...editData.questions];
    if (field === 'is_correct' && value) {
      // Set all options to false first, then set the selected one to true
      updatedQuestions[questionIndex].options.forEach(opt => opt.is_correct = false);
    }
    updatedQuestions[questionIndex].options[optionIndex][field] = value;
    setEditData({ ...editData, questions: updatedQuestions });
  };

  const addNewQuestion = () => {
    const newQuestion = {
      id: Date.now().toString(),
      question_text: '',
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ],
      image_url: null
    };
    setEditData({
      ...editData,
      questions: [...editData.questions, newQuestion]
    });
    setEditingQuestionIndex(editData.questions.length);
  };

  const [deleteQuestionConfirm, setDeleteQuestionConfirm] = useState({ show: false, questionIndex: null });

  const removeQuestion = (questionIndex) => {
    console.log('Attempting to remove question at index:', questionIndex);
    console.log('Current questions:', editData.questions);
    
    setDeleteQuestionConfirm({ show: true, questionIndex });
  };

  const confirmRemoveQuestion = () => {
    const { questionIndex } = deleteQuestionConfirm;
    try {
      const updatedQuestions = editData.questions.filter((_, index) => index !== questionIndex);
      console.log('Updated questions after removal:', updatedQuestions);
      
      setEditData({ ...editData, questions: updatedQuestions });
      setEditingQuestionIndex(null);
      setDeleteQuestionConfirm({ show: false, questionIndex: null });
      
      console.log('Question removed successfully');
      alert('Question removed successfully!');
    } catch (error) {
      console.error('Error removing question:', error);
      alert('Error removing question: ' + error.message);
      setDeleteQuestionConfirm({ show: false, questionIndex: null });
    }
  };

  const toggleUserAccess = (userId) => {
    setEditData({
      ...editData,
      allowed_users: editData.allowed_users.includes(userId)
        ? editData.allowed_users.filter(id => id !== userId)
        : [...editData.allowed_users, userId]
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate questions
    for (let i = 0; i < editData.questions.length; i++) {
      const question = editData.questions[i];
      if (!question.question_text || !question.options.every(opt => opt.text) || !question.options.some(opt => opt.is_correct)) {
        alert(`Question ${i + 1} is incomplete. Please fill all fields and select correct answer.`);
        return;
      }
    }
    
    if (editData.questions.length === 0) {
      alert('Please add at least one question');
      return;
    }

    onUpdate(quiz.id, editData);
  };

  const getSubcategories = () => {
    return predefinedSubjects[editData.subject] || ['General'];
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 my-8 max-h-screen overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-semibold">Edit Quiz: {quiz.title}</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ✕
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Quiz Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Title</label>
              <input
                type="text"
                value={editData.title}
                onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg"
                required
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">Category</label>
              <input
                type="text"
                value={editData.category}
                onChange={(e) => setEditData({ ...editData, category: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Description</label>
            <textarea
              value={editData.description}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
              rows="3"
              required
            />
          </div>

          {/* Subject Structure */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Subject</label>
              <select
                value={editData.subject}
                onChange={(e) => setEditData({ ...editData, subject: e.target.value, subcategory: 'General' })}
                className="w-full p-3 border border-gray-300 rounded-lg"
              >
                {Object.keys(predefinedSubjects).map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">Subcategory</label>
              <select
                value={editData.subcategory}
                onChange={(e) => setEditData({ ...editData, subcategory: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg"
              >
                {getSubcategories().map(subcategory => (
                  <option key={subcategory} value={subcategory}>{subcategory}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Quiz Settings */}
          <div className="flex flex-wrap items-center space-x-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={editData.is_public}
                onChange={(e) => setEditData({ ...editData, is_public: e.target.checked, allowed_users: [] })}
                className="mr-2"
              />
              Public Quiz
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={editData.is_active}
                onChange={(e) => setEditData({ ...editData, is_active: e.target.checked })}
                className="mr-2"
              />
              Active
            </label>
          </div>

          {/* User Access Control */}
          {editData.is_public && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="block text-gray-700 font-semibold mb-2">
                Select Users Who Can Access This Quiz ({editData.allowed_users.length} selected)
              </label>
              <div className="max-h-32 overflow-y-auto border border-gray-300 rounded-lg p-3">
                {allUsers.map((user) => (
                  <div key={user.id} className="flex items-center mb-2">
                    <input
                      type="checkbox"
                      checked={editData.allowed_users.includes(user.id)}
                      onChange={() => toggleUserAccess(user.id)}
                      className="mr-3"
                    />
                    <span className="text-sm">{user.name} ({user.email})</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Questions Section */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-semibold">Questions ({editData.questions.length})</h4>
              <button
                type="button"
                onClick={addNewQuestion}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition duration-200"
              >
                ➕ Add Question
              </button>
            </div>

            <div className="space-y-4">
              {editData.questions.map((question, questionIndex) => (
                <div key={questionIndex} className="border border-gray-300 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-3">
                    <h5 className="font-semibold">Question {questionIndex + 1}</h5>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setEditingQuestionIndex(editingQuestionIndex === questionIndex ? null : questionIndex)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        {editingQuestionIndex === questionIndex ? '📝 Editing' : '✏️ Edit'}
                      </button>
                      <button
                        type="button"
                        onClick={() => removeQuestion(questionIndex)}
                        className="text-red-600 hover:text-red-800"
                      >
                        🗑️ Remove
                      </button>
                    </div>
                  </div>

                  {editingQuestionIndex === questionIndex ? (
                    // Edit Mode
                    <div className="space-y-4">
                      <input
                        type="text"
                        value={question.question_text}
                        onChange={(e) => updateQuestion(questionIndex, 'question_text', e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg"
                        placeholder="Enter question text"
                      />

                      {/* Image Upload */}
                      <div>
                        {question.image_url ? (
                          <div className="relative inline-block">
                            <img
                              src={question.image_url}
                              alt="Question"
                              className="max-w-xs h-auto rounded-lg shadow"
                            />
                            <button
                              type="button"
                              onClick={() => removeImage(questionIndex)}
                              className="absolute top-2 right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-700"
                            >
                              ✕
                            </button>
                          </div>
                        ) : (
                          <div>
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => handleImageUpload(e, questionIndex)}
                              className="hidden"
                              id={`imageUpload-${questionIndex}`}
                              disabled={uploadingImage}
                            />
                            <label
                              htmlFor={`imageUpload-${questionIndex}`}
                              className="cursor-pointer inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200 text-sm"
                            >
                              {uploadingImage ? 'Uploading...' : '📷 Add Image'}
                            </label>
                          </div>
                        )}
                      </div>

                      {/* Options */}
                      <div className="space-y-2">
                        {question.options.map((option, optionIndex) => (
                          <div key={optionIndex} className="flex items-center space-x-3">
                            <input
                              type="radio"
                              name={`correct-${questionIndex}`}
                              checked={option.is_correct}
                              onChange={() => updateQuestionOption(questionIndex, optionIndex, 'is_correct', true)}
                            />
                            <input
                              type="text"
                              value={option.text}
                              onChange={(e) => updateQuestionOption(questionIndex, optionIndex, 'text', e.target.value)}
                              className="flex-1 p-2 border border-gray-300 rounded-lg"
                              placeholder={`Option ${String.fromCharCode(65 + optionIndex)}`}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    // Display Mode
                    <div>
                      <p className="mb-3">{question.question_text}</p>
                      {question.image_url && (
                        <img src={question.image_url} alt="Question" className="max-w-xs h-auto rounded-lg shadow mb-3" />
                      )}
                      <div className="grid grid-cols-2 gap-2">
                        {question.options.map((option, optionIndex) => (
                          <div
                            key={optionIndex}
                            className={`p-2 rounded text-sm ${
                              option.is_correct ? 'bg-green-100 text-green-800' : 'bg-gray-100'
                            }`}
                          >
                            {String.fromCharCode(65 + optionIndex)}. {option.text}
                            {option.is_correct && ' ✓'}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-4 pt-6 border-t">
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition duration-200 font-semibold"
            >
              💾 Update Quiz
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
            >
              Cancel
            </button>
          </div>
        </form>

        {/* Question Deletion Confirmation Modal */}
        {deleteQuestionConfirm.show && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <div className="text-center mb-6">
                <div className="text-4xl mb-4">🗑️</div>
                <h3 className="text-lg font-semibold mb-2">Remove Question?</h3>
                <p className="text-gray-600 text-sm">
                  Are you sure you want to remove Question {deleteQuestionConfirm.questionIndex + 1}?
                </p>
                <p className="text-red-600 text-sm mt-2">
                  ⚠️ This action cannot be undone.
                </p>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={confirmRemoveQuestion}
                  className="flex-1 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition duration-200 font-semibold"
                >
                  Yes, Remove
                </button>
                <button
                  onClick={() => setDeleteQuestionConfirm({ show: false, questionIndex: null })}
                  className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Admin Categories View with Global Subject Management
function AdminCategoriesView({ categories, fetchCategories }) {
  const [activeTab, setActiveTab] = useState('global-subjects');
  const [globalSubjects, setGlobalSubjects] = useState([]);
  const [showCreateGlobalModal, setShowCreateGlobalModal] = useState(false);
  const [newGlobalSubject, setNewGlobalSubject] = useState({ name: '', description: '', subfolders: [''] });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState({ show: false, subjectId: null, subjectName: '' });

  useEffect(() => {
    if (activeTab === 'global-subjects') {
      fetchGlobalSubjects();
    }
  }, [activeTab]);

  const fetchGlobalSubjects = async () => {
    try {
      const response = await apiCall('/admin/global-subjects');
      setGlobalSubjects(response.data);
    } catch (error) {
      console.error('Error fetching global subjects:', error);
    }
  };

  const createGlobalSubject = async () => {
    if (!newGlobalSubject.name.trim()) {
      alert('Subject name is required');
      return;
    }

    const subjectData = {
      name: newGlobalSubject.name.trim(),
      description: newGlobalSubject.description.trim(),
      subfolders: newGlobalSubject.subfolders.filter(sf => sf.trim()).map(sf => sf.trim())
    };

    try {
      await apiCall('/admin/global-subject', {
        method: 'POST',
        data: subjectData
      });
      setShowCreateGlobalModal(false);
      setNewGlobalSubject({ name: '', description: '', subfolders: [''] });
      fetchGlobalSubjects();
      alert('Global subject created successfully!');
    } catch (error) {
      alert('Error creating global subject: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteGlobalSubject = (subjectId, subjectName) => {
    setShowDeleteConfirm({ show: true, subjectId, subjectName });
  };

  const confirmDeleteGlobalSubject = async () => {
    try {
      await apiCall(`/admin/global-subject/${showDeleteConfirm.subjectId}`, {
        method: 'DELETE'
      });
      setShowDeleteConfirm({ show: false, subjectId: null, subjectName: '' });
      fetchGlobalSubjects();
      alert('Global subject deleted successfully!');
    } catch (error) {
      alert('Error deleting global subject: ' + (error.response?.data?.detail || error.message));
    }
  };

  const addSubfolder = () => {
    setNewGlobalSubject({
      ...newGlobalSubject,
      subfolders: [...newGlobalSubject.subfolders, '']
    });
  };

  const updateSubfolder = (index, value) => {
    const updatedSubfolders = [...newGlobalSubject.subfolders];
    updatedSubfolders[index] = value;
    setNewGlobalSubject({
      ...newGlobalSubject,
      subfolders: updatedSubfolders
    });
  };

  const removeSubfolder = (index) => {
    if (newGlobalSubject.subfolders.length > 1) {
      const updatedSubfolders = newGlobalSubject.subfolders.filter((_, i) => i !== index);
      setNewGlobalSubject({
        ...newGlobalSubject,
        subfolders: updatedSubfolders
      });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Subject & Category Management</h2>
        {activeTab === 'global-subjects' && (
          <button
            onClick={() => setShowCreateGlobalModal(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition duration-200"
          >
            ➕ Create Global Subject
          </button>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 border-b">
        <button
          onClick={() => setActiveTab('global-subjects')}
          className={`px-4 py-2 font-semibold transition duration-200 border-b-2 ${
            activeTab === 'global-subjects'
              ? 'text-indigo-600 border-indigo-600'
              : 'text-gray-500 border-transparent hover:text-gray-700'
          }`}
        >
          🌐 Global Subjects & Subfolders
        </button>
        <button
          onClick={() => setActiveTab('quiz-categories')}
          className={`px-4 py-2 font-semibold transition duration-200 border-b-2 ${
            activeTab === 'quiz-categories'
              ? 'text-indigo-600 border-indigo-600'
              : 'text-gray-500 border-transparent hover:text-gray-700'
          }`}
        >
          📂 Legacy Quiz Categories
        </button>
      </div>

      {/* Global Subjects Tab */}
      {activeTab === 'global-subjects' && (
        <div>
          <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-400 rounded">
            <p className="text-blue-800 text-sm">
              <strong>Global Subjects & Subfolders:</strong> These will be available to all users (admin and regular users) when creating quizzes. 
              They serve as the standardized category system for the entire platform.
            </p>
          </div>

          {globalSubjects.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg mb-4">No global subjects created yet.</p>
              <button
                onClick={() => setShowCreateGlobalModal(true)}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition duration-200"
              >
                Create Your First Global Subject
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {globalSubjects.map((subject) => (
                <div key={subject.id} className="border rounded-lg p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-800 flex items-center">
                        🌐 {subject.name}
                      </h3>
                      {subject.description && (
                        <p className="text-gray-600 mt-1">{subject.description}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-2">
                        Created: {new Date(subject.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={() => deleteGlobalSubject(subject.id, subject.name)}
                      className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition duration-200"
                    >
                      🗑️ Delete
                    </button>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-700 mb-2">
                      📁 Subfolders ({subject.subfolders?.length || 0}):
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                      {subject.subfolders?.map((subfolder) => (
                        <div
                          key={subfolder.id}
                          className="bg-white border rounded-lg p-3 text-center shadow-sm"
                        >
                          <span className="text-sm font-medium text-gray-700">
                            {subfolder.name}
                          </span>
                        </div>
                      )) || <p className="text-gray-500 text-sm">No subfolders</p>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Legacy Quiz Categories Tab */}
      {activeTab === 'quiz-categories' && (
        <div>
          <div className="mb-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
            <p className="text-yellow-800 text-sm">
              <strong>Legacy Categories:</strong> These are the old category system. Consider migrating to the new Global Subjects system for better organization.
            </p>
          </div>
          
          {categories.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No legacy categories found.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categories.map((category) => (
                <div key={category.id} className="border rounded-lg p-4">
                  <h3 className="font-semibold text-gray-800">{category.name}</h3>
                  {category.description && (
                    <p className="text-gray-600 text-sm mt-2">{category.description}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    Created: {new Date(category.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create Global Subject Modal */}
      {showCreateGlobalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">Create Global Subject</h3>
              <button
                onClick={() => setShowCreateGlobalModal(false)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 font-semibold mb-2">Subject Name *</label>
                <input
                  type="text"
                  value={newGlobalSubject.name}
                  onChange={(e) => setNewGlobalSubject({ ...newGlobalSubject, name: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-lg"
                  placeholder="e.g., Advanced Mathematics"
                  required
                />
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Description</label>
                <textarea
                  value={newGlobalSubject.description}
                  onChange={(e) => setNewGlobalSubject({ ...newGlobalSubject, description: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-lg"
                  rows="3"
                  placeholder="Brief description of this subject area"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Subfolders</label>
                <div className="space-y-2">
                  {newGlobalSubject.subfolders.map((subfolder, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={subfolder}
                        onChange={(e) => updateSubfolder(index, e.target.value)}
                        className="flex-1 p-2 border border-gray-300 rounded"
                        placeholder={`Subfolder ${index + 1}`}
                      />
                      {newGlobalSubject.subfolders.length > 1 && (
                        <button
                          onClick={() => removeSubfolder(index)}
                          className="bg-red-500 text-white px-3 py-2 rounded hover:bg-red-600"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={addSubfolder}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 text-sm"
                  >
                    + Add Subfolder
                  </button>
                </div>
              </div>
            </div>

            <div className="flex gap-4 pt-6">
              <button
                onClick={createGlobalSubject}
                className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
              >
                🌐 Create Global Subject
              </button>
              <button
                onClick={() => setShowCreateGlobalModal(false)}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">🗑️</div>
              <h3 className="text-lg font-semibold mb-2">Delete Global Subject?</h3>
              <p className="text-gray-600 text-sm">
                Are you sure you want to delete "{showDeleteConfirm.subjectName}"?
              </p>
              <p className="text-red-600 text-sm mt-2">
                ⚠️ This action cannot be undone and will affect all users.
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={confirmDeleteGlobalSubject}
                className="flex-1 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition duration-200 font-semibold"
              >
                Yes, Delete
              </button>
              <button
                onClick={() => setShowDeleteConfirm({ show: false, subjectId: null, subjectName: '' })}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function AdminCreateQuiz({ setCurrentView }) {
  const [quiz, setQuiz] = useState({
    title: '',
    description: '',
    category: '',
    subject: '', // Will be set dynamically when subjects are loaded
    subcategory: 'General',
    is_public: false,
    allowed_users: [],
    questions: [],
    min_pass_percentage: 60.0,
    time_limit_minutes: null,
    shuffle_questions: false,
    shuffle_options: false
  });

  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: '',
    question_type: 'multiple_choice',
    points: 1,
    difficulty: 'medium',
    is_mandatory: true,
    explanation: '',
    multiple_correct: false,
    options: [
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ],
    open_ended_answer: {
      expected_answers: [''],
      keywords: [],
      case_sensitive: false,
      partial_credit: true
    },
    image_url: null,
    pdf_url: null
  });

  const [uploadingFile, setUploadingFile] = useState(false);
  const [allUsers, setAllUsers] = useState([]);
  const [predefinedSubjects, setPredefinedSubjects] = useState({});
  const [validationErrors, setValidationErrors] = useState([]);
  const [showPreview, setShowPreview] = useState(false);
  
  // Publish modal state
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [createdQuizData, setCreatedQuizData] = useState(null);
  const [publishingQuiz, setPublishingQuiz] = useState(false);

  useEffect(() => {
    fetchPredefinedSubjects();
    if (quiz.is_public) {
      fetchAllUsers();
    }
  }, [quiz.is_public]);

  useEffect(() => {
    // Update quiz subject when predefined subjects are loaded
    const availableSubjects = Object.keys(predefinedSubjects);
    if (availableSubjects.length > 0 && !availableSubjects.includes(quiz.subject)) {
      setQuiz(prev => ({
        ...prev,
        subject: availableSubjects[0],
        subcategory: 'General'
      }));
    }
  }, [predefinedSubjects]);

  const fetchPredefinedSubjects = async () => {
    try {
      const response = await apiCall('/admin/predefined-subjects');
      setPredefinedSubjects(response.data);
    } catch (error) {
      console.error('Error fetching subjects:', error);
      setPredefinedSubjects({});
    }
  };

  const fetchAllUsers = async () => {
    try {
      const response = await apiCall('/admin/users');
      setAllUsers(response.data.filter(user => user.role === 'user'));
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setUploadingFile(true);
      const response = await apiCall('/admin/upload-file', {
        method: 'POST',
        data: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      return response.data;
    } catch (error) {
      alert('Error uploading file: ' + (error.response?.data?.detail || 'Unknown error'));
      return null;
    } finally {
      setUploadingFile(false);
    }
  };

  const handleFileUpload = async (event, fileType) => {
    const file = event.target.files[0];
    if (!file) return;

    const allowedTypes = fileType === 'image' 
      ? ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
      : ['application/pdf'];

    if (!allowedTypes.includes(file.type)) {
      alert(`Please select a valid ${fileType} file`);
      return;
    }

    const maxSize = fileType === 'image' ? 5 * 1024 * 1024 : 10 * 1024 * 1024;
    if (file.size > maxSize) {
      alert(`File size must be less than ${fileType === 'image' ? '5MB' : '10MB'}`);
      return;
    }

    const fileData = await uploadFile(file);
    if (fileData) {
      const fieldName = fileType === 'image' ? 'image_url' : 'pdf_url';
      setCurrentQuestion({ ...currentQuestion, [fieldName]: fileData.url });
    }
  };

  const removeFile = (fileType) => {
    const fieldName = fileType === 'image' ? 'image_url' : 'pdf_url';
    setCurrentQuestion({ ...currentQuestion, [fieldName]: null });
  };

  const addOption = () => {
    if (currentQuestion.options.length < 6) {
      setCurrentQuestion({
        ...currentQuestion,
        options: [...currentQuestion.options, { text: '', is_correct: false }]
      });
    }
  };

  const removeOption = (index) => {
    if (currentQuestion.options.length > 2) {
      const updatedOptions = currentQuestion.options.filter((_, i) => i !== index);
      setCurrentQuestion({ ...currentQuestion, options: updatedOptions });
    }
  };

  const updateOption = (index, field, value) => {
    const updatedOptions = [...currentQuestion.options];
    if (field === 'is_correct' && value && !currentQuestion.multiple_correct) {
      // Single correct answer - uncheck all others
      updatedOptions.forEach(opt => opt.is_correct = false);
    }
    updatedOptions[index][field] = value;
    setCurrentQuestion({ ...currentQuestion, options: updatedOptions });
  };

  const updateOpenEndedAnswer = (field, value) => {
    setCurrentQuestion({
      ...currentQuestion,
      open_ended_answer: {
        ...currentQuestion.open_ended_answer,
        [field]: value
      }
    });
  };

  const addExpectedAnswer = () => {
    const updatedAnswers = [...currentQuestion.open_ended_answer.expected_answers, ''];
    updateOpenEndedAnswer('expected_answers', updatedAnswers);
  };

  const updateExpectedAnswer = (index, value) => {
    const updatedAnswers = [...currentQuestion.open_ended_answer.expected_answers];
    updatedAnswers[index] = value;
    updateOpenEndedAnswer('expected_answers', updatedAnswers);
  };

  const removeExpectedAnswer = (index) => {
    if (currentQuestion.open_ended_answer.expected_answers.length > 1) {
      const updatedAnswers = currentQuestion.open_ended_answer.expected_answers.filter((_, i) => i !== index);
      updateOpenEndedAnswer('expected_answers', updatedAnswers);
    }
  };

  const validateCurrentQuestion = () => {
    const errors = [];
    
    if (!currentQuestion.question_text || currentQuestion.question_text.length < 5) {
      errors.push('Question text must be at least 5 characters long');
    }
    
    if (currentQuestion.points <= 0) {
      errors.push('Points must be positive');
    }
    
    if (currentQuestion.question_type === 'multiple_choice') {
      if (currentQuestion.options.length < 2) {
        errors.push('Multiple choice questions must have at least 2 options');
      }
      
      if (!currentQuestion.options.every(opt => opt.text.trim())) {
        errors.push('All options must have text');
      }
      
      if (!currentQuestion.options.some(opt => opt.is_correct)) {
        errors.push('At least one option must be correct');
      }
    } else if (currentQuestion.question_type === 'open_ended') {
      if (!currentQuestion.open_ended_answer.expected_answers.some(ans => ans.trim())) {
        errors.push('At least one expected answer is required');
      }
    }
    
    return errors;
  };

  const addQuestion = () => {
    const errors = validateCurrentQuestion();
    if (errors.length > 0) {
      alert('Please fix the following errors:\\n' + errors.join('\\n'));
      return;
    }

    setQuiz({
      ...quiz,
      questions: [...quiz.questions, { ...currentQuestion, id: Date.now().toString() }]
    });
    
    // Reset form
    setCurrentQuestion({
      question_text: '',
      question_type: 'multiple_choice',
      points: 1,
      difficulty: 'medium',
      is_mandatory: true,
      explanation: '',
      multiple_correct: false,
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ],
      open_ended_answer: {
        expected_answers: [''],
        keywords: [],
        case_sensitive: false,
        partial_credit: true
      },
      image_url: null,
      pdf_url: null
    });
  };

  const validateQuiz = () => {
    const errors = [];
    
    // Check if subjects are available
    if (Object.keys(predefinedSubjects).length === 0) {
      errors.push('No subjects available. Please create subjects first in the Categories section.');
    }
    
    if (!quiz.title || quiz.title.length < 3) {
      errors.push('Title must be at least 3 characters long');
    }
    
    if (!quiz.description || quiz.description.length < 10) {
      errors.push('Description must be at least 10 characters long');
    }
    
    if (!quiz.category || quiz.category.length < 2) {
      errors.push('Category is required');
    }
    
    if (!quiz.subject) {
      errors.push('Subject is required');
    }
    
    if (quiz.questions.length === 0) {
      errors.push('At least one question is required');
    }
    
    if (quiz.is_public && quiz.allowed_users.length === 0) {
      errors.push('Please select at least one user for public quiz access');
    }
    
    return errors;
  };

  const createQuiz = async () => {
    const errors = validateQuiz();
    setValidationErrors(errors);
    
    if (errors.length > 0) {
      alert('Please fix validation errors before creating quiz');
      return;
    }

    try {
      const response = await apiCall('/admin/quiz', {
        method: 'POST',
        data: quiz
      });
      
      const createdQuiz = response.data;
      
      // Show enhanced publish modal instead of basic confirm
      setCreatedQuizData(createdQuiz);
      setShowPublishModal(true);
      
    } catch (error) {
      if (error.response?.status === 400) {
        const errorData = error.response.data;
        if (errorData.detail && errorData.detail.errors) {
          setValidationErrors(errorData.detail.errors);
          alert('Quiz validation failed. Please check the errors.');
        } else {
          alert('Error creating quiz: ' + (errorData.detail || 'Unknown error'));
        }
      } else {
        alert('Error creating quiz: ' + (error.response?.data?.detail || 'Unknown error'));
      }
    }
  };

  // Enhanced publish handlers
  const handlePublishQuiz = async () => {
    setPublishingQuiz(true);
    try {
      await apiCall(`/admin/quiz/${createdQuizData.id}/publish`, {
        method: 'POST'
      });
      setShowPublishModal(false);
      setPublishingQuiz(false);
      alert('🎉 SUCCESS! Quiz published and ready for users!');
      setCurrentView('quizzes');
    } catch (publishError) {
      setPublishingQuiz(false);
      alert('⚠️ Quiz created but failed to publish: ' + (publishError.response?.data?.detail || 'Unknown error') + '\n\nYou can publish it from the Quiz Management page.');
      setCurrentView('quizzes');
    }
  };

  const handleKeepAsDraft = () => {
    setShowPublishModal(false);
    alert('📝 Quiz saved as DRAFT. Remember to publish it from the Quiz Management page when ready!');
    setCurrentView('quizzes');
  };

  const toggleUserAccess = (userId) => {
    setQuiz({
      ...quiz,
      allowed_users: quiz.allowed_users.includes(userId)
        ? quiz.allowed_users.filter(id => id !== userId)
        : [...quiz.allowed_users, userId]
    });
  };

  const getSubcategories = () => {
    return predefinedSubjects[quiz.subject] || ['General'];
  };

  const getTotalPoints = () => {
    return quiz.questions.reduce((total, q) => total + q.points, 0);
  };

  const [deleteQuestionFromQuizConfirm, setDeleteQuestionFromQuizConfirm] = useState({ show: false, questionIndex: null });

  const removeQuestionFromQuiz = (questionIndex) => {
    console.log('Attempting to remove question at index:', questionIndex);
    setDeleteQuestionFromQuizConfirm({ show: true, questionIndex });
  };

  const confirmRemoveQuestionFromQuiz = () => {
    const { questionIndex } = deleteQuestionFromQuizConfirm;
    try {
      const updatedQuestions = quiz.questions.filter((_, index) => index !== questionIndex);
      console.log('Updated questions after removal:', updatedQuestions);
      
      setQuiz({ ...quiz, questions: updatedQuestions });
      setDeleteQuestionFromQuizConfirm({ show: false, questionIndex: null });
      
      console.log('Question removed successfully from quiz creation');
      alert('Question removed successfully!');
    } catch (error) {
      console.error('Error removing question:', error);
      alert('Error removing question: ' + error.message);
      setDeleteQuestionFromQuizConfirm({ show: false, questionIndex: null });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Create Advanced Quiz</h2>
      
      {/* No Subjects Warning */}
      {Object.keys(predefinedSubjects).length === 0 && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="text-yellow-800 font-semibold mb-2">📝 Create Subjects First</h4>
          <p className="text-yellow-700 text-sm mb-3">
            No subjects are available for quiz creation. You need to create subjects and subfolders first.
          </p>
          <button
            onClick={() => setCurrentView('categories')}
            className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition duration-200 text-sm"
          >
            📚 Go to Categories & Subjects
          </button>
        </div>
      )}
      
      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="text-red-800 font-semibold mb-2">⚠️ Validation Errors:</h4>
          <ul className="list-disc list-inside text-red-700 text-sm">
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Basic Quiz Info */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-gray-700 font-semibold mb-2">
            Quiz Title *
          </label>
          <input
            type="text"
            value={quiz.title}
            onChange={(e) => setQuiz({ ...quiz, title: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg"
            placeholder="Enter quiz title (min 3 characters)"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-semibold mb-2">
            Description *
          </label>
          <textarea
            value={quiz.description}
            onChange={(e) => setQuiz({ ...quiz, description: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg"
            rows="3"
            placeholder="Describe your quiz (min 10 characters)"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Subject *</label>
            {Object.keys(predefinedSubjects).length > 0 ? (
              <select
                value={quiz.subject}
                onChange={(e) => setQuiz({ ...quiz, subject: e.target.value, subcategory: 'General' })}
                className="w-full p-3 border border-gray-300 rounded-lg"
              >
                {Object.keys(predefinedSubjects).map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            ) : (
              <div className="w-full p-3 border border-orange-300 bg-orange-50 rounded-lg">
                <p className="text-orange-700 text-sm">
                  ⚠️ No subjects available. Please create subjects first in the Categories section.
                </p>
              </div>
            )}
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Subcategory</label>
            {Object.keys(predefinedSubjects).length > 0 ? (
              <select
                value={quiz.subcategory}
                onChange={(e) => setQuiz({ ...quiz, subcategory: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg"
              >
                {getSubcategories().map(subcategory => (
                  <option key={subcategory} value={subcategory}>{subcategory}</option>
                ))}
              </select>
            ) : (
              <div className="w-full p-3 border border-gray-300 bg-gray-50 rounded-lg">
                <p className="text-gray-500 text-sm">No subcategories available</p>
              </div>
            )}
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Category *</label>
            <input
              type="text"
              value={quiz.category}
              onChange={(e) => setQuiz({ ...quiz, category: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
              placeholder="Specific topic"
            />
          </div>
        </div>

        {/* Quiz Settings */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-3">Quiz Settings</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Pass Percentage (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={quiz.min_pass_percentage}
                onChange={(e) => setQuiz({ ...quiz, min_pass_percentage: parseFloat(e.target.value) || 0 })}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Time Limit (minutes)</label>
              <input
                type="number"
                min="1"
                value={quiz.time_limit_minutes || ''}
                onChange={(e) => setQuiz({ ...quiz, time_limit_minutes: e.target.value ? parseInt(e.target.value) : null })}
                className="w-full p-3 border border-gray-300 rounded-lg"
                placeholder="Optional"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-4 mt-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={quiz.shuffle_questions}
                onChange={(e) => setQuiz({ ...quiz, shuffle_questions: e.target.checked })}
                className="mr-2"
              />
              Shuffle Questions
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={quiz.shuffle_options}
                onChange={(e) => setQuiz({ ...quiz, shuffle_options: e.target.checked })}
                className="mr-2"
              />
              Shuffle Options
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={quiz.is_public}
                onChange={(e) => setQuiz({ ...quiz, is_public: e.target.checked, allowed_users: [] })}
                className="mr-2"
              />
              Public Quiz
            </label>
          </div>

          {quiz.is_public && (
            <div className="mt-4">
              <label className="block text-gray-700 font-semibold mb-2">
                Select Users ({quiz.allowed_users.length} selected)
              </label>
              <div className="max-h-32 overflow-y-auto border border-gray-300 rounded-lg p-3">
                {allUsers.map((user) => (
                  <div key={user.id} className="flex items-center mb-2">
                    <input
                      type="checkbox"
                      checked={quiz.allowed_users.includes(user.id)}
                      onChange={() => toggleUserAccess(user.id)}
                      className="mr-3"
                    />
                    <span className="text-sm">{user.name} ({user.email})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Question Creation Form */}
      <QuestionCreationForm
        currentQuestion={currentQuestion}
        setCurrentQuestion={setCurrentQuestion}
        uploadingFile={uploadingFile}
        handleFileUpload={handleFileUpload}
        removeFile={removeFile}
        addOption={addOption}
        removeOption={removeOption}
        updateOption={updateOption}
        updateOpenEndedAnswer={updateOpenEndedAnswer}
        addExpectedAnswer={addExpectedAnswer}
        updateExpectedAnswer={updateExpectedAnswer}
        removeExpectedAnswer={removeExpectedAnswer}
        validateCurrentQuestion={validateCurrentQuestion}
        addQuestion={addQuestion}
      />

      {/* Questions Preview */}
      {quiz.questions.length > 0 && (
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">
              Questions Added ({quiz.questions.length}) - Total Points: {getTotalPoints()}
            </h3>
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="text-blue-600 hover:text-blue-800 font-semibold"
            >
              {showPreview ? '👁️ Hide Preview' : '👀 Show Preview'}
            </button>
          </div>

          {showPreview && (
            <div className="space-y-4">
              {quiz.questions.map((question, index) => (
                <QuestionPreview 
                  key={index} 
                  question={question} 
                  index={index} 
                  onDelete={removeQuestionFromQuiz}
                />
              ))}
            </div>
          )}
        </div>
      )}

      <div className="flex gap-4">
        <button
          onClick={createQuiz}
          className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
        >
          🚀 Create Advanced Quiz
        </button>
        <button
          onClick={() => setCurrentView('quizzes')}
          className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
        >
          Cancel
        </button>
      </div>

      {/* Question Deletion Confirmation Modal for Quiz Creation */}
      {deleteQuestionFromQuizConfirm.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">🗑️</div>
              <h3 className="text-lg font-semibold mb-2">Remove Question?</h3>
              <p className="text-gray-600 text-sm">
                Are you sure you want to remove Question {deleteQuestionFromQuizConfirm.questionIndex + 1}?
              </p>
              <p className="text-red-600 text-sm mt-2">
                ⚠️ This action cannot be undone.
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={confirmRemoveQuestionFromQuiz}
                className="flex-1 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition duration-200 font-semibold"
              >
                Yes, Remove
              </button>
              <button
                onClick={() => setDeleteQuestionFromQuizConfirm({ show: false, questionIndex: null })}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Publish Modal - Defaults to Publish */}
      {showPublishModal && createdQuizData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">🎉</div>
              <h3 className="text-xl font-semibold mb-2 text-green-600">Quiz Created Successfully!</h3>
              <p className="text-gray-800 font-medium mb-2">
                "{createdQuizData.title}"
              </p>
            </div>

            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-orange-600">⚠️</span>
                <span className="font-semibold text-orange-800">IMPORTANT: Quiz Publishing</span>
              </div>
              <p className="text-sm text-orange-700 mb-2">
                Your quiz is currently in <strong>DRAFT MODE</strong>. Users cannot take this quiz until it's published.
              </p>
              <div className="bg-orange-100 p-2 rounded text-xs text-orange-800">
                📝 Draft Mode: Quiz is saved but not accessible to users<br />
                🚀 Published: Quiz is live and available for users to take
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-green-600">🚀</span>
                <span className="font-semibold text-green-800">Recommended Action</span>
              </div>
              <p className="text-sm text-green-700">
                <strong>Publish Now</strong> to make your quiz available immediately. This is the most common choice.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handlePublishQuiz}
                disabled={publishingQuiz}
                className="flex-1 bg-green-600 text-white py-4 rounded-lg hover:bg-green-700 transition duration-200 font-semibold text-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {publishingQuiz ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="animate-spin">⏳</span>
                    Publishing...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    🚀 Publish Quiz Now
                    <span className="text-xs bg-green-500 px-2 py-1 rounded">RECOMMENDED</span>
                  </span>
                )}
              </button>
              <button
                onClick={handleKeepAsDraft}
                disabled={publishingQuiz}
                className="flex-1 bg-gray-600 text-white py-4 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                📝 Keep as Draft
              </button>
            </div>

            <div className="text-center mt-4">
              <p className="text-xs text-gray-500">
                💡 You can always publish draft quizzes later from the Quiz Management page
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// User Dashboard
function UserDashboard({ currentView, setCurrentView }) {
  const { user, logout } = useAuth();
  const [quizzes, setQuizzes] = useState([]);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);
  const [quizResult, setQuizResult] = useState(null);
  const [myAttempts, setMyAttempts] = useState([]);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [isSubmittingQuiz, setIsSubmittingQuiz] = useState(false);
  const [quizError, setQuizError] = useState(null);
  const [isTimedQuiz, setIsTimedQuiz] = useState(false);

  useEffect(() => {
    if (currentView === 'home') fetchQuizzes();
    if (currentView === 'my-attempts') fetchMyAttempts();
  }, [currentView]);

  const fetchQuizzes = async () => {
    try {
      const response = await apiCall('/quizzes');
      setQuizzes(response.data);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    }
  };

  const fetchMyAttempts = async () => {
    try {
      const response = await apiCall('/my-attempts');
      setMyAttempts(response.data);
    } catch (error) {
      console.error('Error fetching attempts:', error);
    }
  };

  const startQuiz = (quiz) => {
    setSelectedQuiz(quiz);
    setCurrentQuestionIndex(0);
    setUserAnswers([]);
    setQuizResult(null);
    setIsTimedQuiz(false);
    setCurrentView('take-quiz');
  };

  const startRealTimeQuiz = (quiz) => {
    setSelectedQuiz(quiz);
    setCurrentQuestionIndex(0);
    setUserAnswers([]);
    setQuizResult(null);
    setIsTimedQuiz(true);
    setCurrentView('realtime-quiz');
  };

  const selectAnswer = (optionText) => {
    const updatedAnswers = [...userAnswers];
    updatedAnswers[currentQuestionIndex] = optionText;
    setUserAnswers(updatedAnswers);
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < selectedQuiz.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      submitQuiz();
    }
  };

  const submitQuiz = async () => {
    console.log('🎯 Starting quiz submission...');
    console.log('Quiz ID:', selectedQuiz.id);
    console.log('User answers:', userAnswers);
    
    setIsSubmittingQuiz(true);
    setQuizError(null); // Clear any previous errors
    
    try {
      console.log('📡 Making API call to:', `/quiz/${selectedQuiz.id}/attempt`);
      
      const response = await apiCall(`/quiz/${selectedQuiz.id}/attempt`, {
        method: 'POST',
        data: {
          quiz_id: selectedQuiz.id,
          answers: userAnswers
        }
      });
      
      console.log('✅ Quiz submission successful:', response.data);
      
      // Verify we have valid result data
      if (!response.data || typeof response.data.score === 'undefined') {
        throw new Error('Invalid response data received from server');
      }
      
      setQuizResult(response.data);
      setCurrentView('result');
      
    } catch (error) {
      console.error('❌ Quiz submission failed:', error);
      
      let errorMessage = 'Unknown error occurred';
      
      // Handle different types of errors
      if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        errorMessage = 'Network error: Unable to reach the server. Please check your internet connection and try again.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Quiz not found or not published yet. Please contact the administrator.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to take this quiz.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      // Set error state instead of using alert (which is blocked)
      setQuizError(errorMessage);
      
      // Do NOT proceed to results page on error
      console.log('🔄 Staying on quiz page due to submission error');
    } finally {
      setIsSubmittingQuiz(false);
    }
  };

  if (currentView === 'take-quiz') {
    return <UserTakeQuiz 
      quiz={selectedQuiz}
      currentQuestionIndex={currentQuestionIndex}
      setCurrentQuestionIndex={setCurrentQuestionIndex}
      userAnswers={userAnswers}
      selectAnswer={selectAnswer}
      nextQuestion={nextQuestion}
      submitQuiz={submitQuiz}
      setCurrentView={setCurrentView}
      isSubmittingQuiz={isSubmittingQuiz}
      quizError={quizError}
      setQuizError={setQuizError}
    />;
  }

  if (currentView === 'realtime-quiz') {
    return <RealTimeQuizSession 
      quiz={selectedQuiz}
      setCurrentView={setCurrentView}
      user={user}
      setQuizResult={setQuizResult}
      setIsTimedQuiz={setIsTimedQuiz}
    />;
  }

  if (currentView === 'result') {
    return <UserResult 
      result={quizResult}
      quiz={selectedQuiz}
      setCurrentView={setCurrentView}
      startQuiz={startQuiz}
      startRealTimeQuiz={startRealTimeQuiz}
      isTimedQuiz={isTimedQuiz}
    />;
  }

  return (
    <PageTransition className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 py-4 flex flex-col lg:flex-row justify-between items-start lg:items-center">
          <div className="mb-4 lg:mb-0">
            <h1 className="text-xl sm:text-2xl font-bold text-gray-800 dark:text-gray-200">📝 Squiz</h1>
            <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">Xoş gəldin, {user.name}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2 sm:gap-4">
            <DarkModeToggle />
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setCurrentView('home')}
              className={`px-2 sm:px-4 py-2 rounded-lg transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
                currentView === 'home' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <span className="sm:hidden">🏠</span>
              <span className="hidden sm:inline">🏠 Quizzes</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setCurrentView('qa-forum')}
              className={`px-2 sm:px-4 py-2 rounded-lg transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
                currentView === 'qa-forum' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <span className="sm:hidden">💬</span>
              <span className="hidden sm:inline">💬 Q&A</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setCurrentView('activity-feed')}
              className={`px-2 sm:px-4 py-2 rounded-lg transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
                currentView === 'activity-feed' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <span className="sm:hidden">📰</span>
              <span className="hidden sm:inline">📰 Activity</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setCurrentView('profile')}
              className={`px-2 sm:px-4 py-2 rounded-lg transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
                currentView === 'profile' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <span className="sm:hidden">👤</span>
              <span className="hidden sm:inline">👤 Profile</span>
            </motion.button>
            <NotificationBell setCurrentView={setCurrentView} currentView={currentView} />
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setCurrentView('my-attempts')}
              className={`px-2 sm:px-4 py-2 rounded-lg transition duration-200 text-xs sm:text-sm whitespace-nowrap ${
                currentView === 'my-attempts' ? 'bg-indigo-600 dark:bg-indigo-500 text-white' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <span className="sm:hidden">📊</span>
              <span className="hidden sm:inline">📊 Results</span>
            </motion.button>
            {/* User quiz and subject creation removed - admin-only functionality */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowPasswordChange(true)}
              className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 px-2 sm:px-4 py-2 rounded-lg transition duration-200 text-xs sm:text-sm whitespace-nowrap"
            >
              <span className="sm:hidden">🔑</span>
              <span className="hidden sm:inline">🔑 Password</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={logout}
              className="bg-red-600 dark:bg-red-500 text-white px-2 sm:px-4 py-2 rounded-lg hover:bg-red-700 dark:hover:bg-red-600 transition duration-200 text-xs sm:text-sm whitespace-nowrap"
            >
              <span className="sm:hidden">🚪</span>
              <span className="hidden sm:inline">🚪 Logout</span>
            </motion.button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-2 sm:px-4 py-4 sm:py-8">
        {currentView === 'home' && (
          <UserHome quizzes={quizzes} startQuiz={startQuiz} startRealTimeQuiz={startRealTimeQuiz} currentUser={user} />
        )}

        {currentView === 'qa-forum' && (
          <QAForum user={user} />
        )}

        {currentView === 'activity-feed' && (
          <ActivityFeed user={user} />
        )}

        {currentView === 'profile' && (
          <UserProfile user={user} />
        )}

        {currentView === 'notifications' && (
          <NotificationCenter user={user} />
        )}

        {/* User creation components removed - admin-only functionality */}

        {currentView === 'my-attempts' && (
          <div>
            <h2 className="text-3xl font-bold text-gray-800 mb-6">Mənim sınaq nəticələrim</h2>
            {myAttempts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">Nəticələrinin yoxdur hələ</p>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {myAttempts.map((attempt) => (
                  <div key={attempt.id} className="bg-white rounded-lg shadow p-6">
                    <h3 className="font-semibold text-gray-800 mb-2">Test sınağı</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Xal:</span>
                        <span className="font-semibold">{attempt.score}/{attempt.total_questions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Faiz:</span>
                        <span className={`font-semibold ${
                          attempt.percentage >= 80 ? 'text-green-600' :
                          attempt.percentage >= 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {attempt.percentage.toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Tarix:</span>
                        <span>{new Date(attempt.attempted_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Password Change Modal */}
      {showPasswordChange && (
        <PasswordChangeModal 
          onClose={() => setShowPasswordChange(false)} 
          userName={user.name}
        />
      )}
    </PageTransition>
  );
}

// Supporting Components for Advanced Quiz Creation
function QuestionCreationForm({
  currentQuestion,
  setCurrentQuestion,
  uploadingFile,
  handleFileUpload,
  removeFile,
  addOption,
  removeOption,
  updateOption,
  updateOpenEndedAnswer,
  addExpectedAnswer,
  updateExpectedAnswer,
  removeExpectedAnswer,
  validateCurrentQuestion,
  addQuestion
}) {
  const [showCropModal, setShowCropModal] = useState(false);
  const [tempImageSrc, setTempImageSrc] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    // Create temporary image URL for cropping
    const reader = new FileReader();
    reader.onload = (e) => {
      setTempImageSrc(e.target.result);
      setShowCropModal(true);
    };
    reader.readAsDataURL(file);
  };

  const handleCropComplete = (croppedImageData) => {
    setCurrentQuestion({ ...currentQuestion, image_url: croppedImageData });
    setShowCropModal(false);
    setTempImageSrc(null);
  };

  const handleMathPreview = () => {
    // Trigger MathJax to re-render
    if (window.MathJax) {
      window.MathJax.typesetPromise().catch((err) => console.log('MathJax error:', err));
    }
  };

  useEffect(() => {
    // Re-render MathJax when question text changes
    const timer = setTimeout(() => {
      if (window.MathJax) {
        window.MathJax.typesetPromise().catch((err) => console.log('MathJax error:', err));
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [currentQuestion.question_text, currentQuestion.options]);

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-lg mb-6">
      <h3 className="text-lg font-semibold mb-4">Add Question</h3>
      
      {/* Question Type Selection */}
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">Question Type</label>
        <div className="flex flex-col sm:flex-row gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="questionType"
              value="multiple_choice"
              checked={currentQuestion.question_type === 'multiple_choice'}
              onChange={(e) => setCurrentQuestion({ ...currentQuestion, question_type: e.target.value })}
              className="mr-2"
            />
            📝 Çoxlu seçim
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="questionType"
              value="open_ended"
              checked={currentQuestion.question_type === 'open_ended'}
              onChange={(e) => setCurrentQuestion({ ...currentQuestion, question_type: e.target.value })}
              className="mr-2"
            />
            ✏️ Open Ended
          </label>
        </div>
      </div>

      {/* Question Text with Math Support */}
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">
          Question Text *
          <span className="text-xs text-blue-600 ml-2">
            (Math: Use $...$ for inline or $$...$$ for display math)
          </span>
        </label>
        <textarea
          value={currentQuestion.question_text}
          onChange={(e) => {
            setCurrentQuestion({ ...currentQuestion, question_text: e.target.value });
            handleMathPreview();
          }}
          className="w-full p-3 border border-gray-300 rounded-lg text-sm sm:text-base"
          rows="3"
          placeholder="Enter your question (min 5 characters). Example: What is $\\sqrt{16}$?"
        />
        
        {/* Math Preview */}
        {currentQuestion.question_text && (
          <div className="mt-2 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-gray-600 mb-1">Preview:</p>
            <div className="tex2jax_process">
              {renderMathContent(currentQuestion.question_text)}
            </div>
          </div>
        )}
      </div>

      {/* Question Metadata */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
        <div>
          <label className="block text-gray-700 font-semibold mb-2">Points</label>
          <input
            type="number"
            min="1"
            max="10"
            value={currentQuestion.points}
            onChange={(e) => setCurrentQuestion({ ...currentQuestion, points: parseInt(e.target.value) || 1 })}
            className="w-full p-2 sm:p-3 border border-gray-300 rounded-lg text-sm"
          />
        </div>
        
        <div>
          <label className="block text-gray-700 font-semibold mb-2">Difficulty</label>
          <select
            value={currentQuestion.difficulty}
            onChange={(e) => setCurrentQuestion({ ...currentQuestion, difficulty: e.target.value })}
            className="w-full p-2 sm:p-3 border border-gray-300 rounded-lg text-sm"
          >
            <option value="easy">🟢 Asan</option>
            <option value="medium">🟡 Normal</option>
            <option value="hard">🔴 Çətin</option>
          </select>
        </div>
        
        <div className="flex items-center pt-4 sm:pt-8">
          <label className="flex items-center text-sm">
            <input
              type="checkbox"
              checked={currentQuestion.is_mandatory}
              onChange={(e) => setCurrentQuestion({ ...currentQuestion, is_mandatory: e.target.checked })}
              className="mr-2"
            />
            Məcburi
          </label>
        </div>

        {currentQuestion.question_type === 'multiple_choice' && (
          <div className="flex items-center pt-4 sm:pt-8">
            <label className="flex items-center text-sm">
              <input
                type="checkbox"
                checked={currentQuestion.multiple_correct}
                onChange={(e) => setCurrentQuestion({ ...currentQuestion, multiple_correct: e.target.checked })}
                className="mr-2"
              />
              Multiple Correct
            </label>
          </div>
        )}
      </div>

      {/* File Uploads */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        {/* Image Upload with Cropping */}
        <div>
          <label className="block text-gray-700 font-semibold mb-2">Question Image</label>
          {!currentQuestion.image_url ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="imageUpload"
                disabled={uploadingFile}
              />
              <label
                htmlFor="imageUpload"
                className={`cursor-pointer inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition duration-200 text-sm ${
                  uploadingFile ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {uploadingFile ? 'Uploading...' : '📷 Upload & Crop Image'}
              </label>
              <p className="text-xs text-gray-500 mt-1">JPG, PNG, GIF, WEBP (max 5MB)</p>
            </div>
          ) : (
            <div className="relative">
              <img
                src={currentQuestion.image_url}
                alt="Question"
                className="w-full h-32 object-cover rounded-lg"
              />
              <button
                onClick={() => removeFile('image')}
                className="absolute top-1 right-1 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-700"
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* PDF Upload */}
        <div>
          <label className="block text-gray-700 font-semibold mb-2">Question PDF</label>
          {!currentQuestion.pdf_url ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => handleFileUpload(e, 'pdf')}
                className="hidden"
                id="pdfUpload"
                disabled={uploadingFile}
              />
              <label
                htmlFor="pdfUpload"
                className={`cursor-pointer inline-flex items-center px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition duration-200 text-sm ${
                  uploadingFile ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {uploadingFile ? 'Uploading...' : '📄 Upload PDF'}
              </label>
              <p className="text-xs text-gray-500 mt-1">PDF files (max 10MB)</p>
            </div>
          ) : (
            <div className="relative border rounded-lg p-4 bg-red-50">
              <div className="flex items-center">
                <span className="text-2xl mr-2">📄</span>
                <span className="text-sm font-medium">PDF Attached</span>
              </div>
              <button
                onClick={() => removeFile('pdf')}
                className="absolute top-1 right-1 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-700"
              >
                ✕
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Question Type Specific Fields */}
      {currentQuestion.question_type === 'multiple_choice' ? (
        <MultipleChoiceQuestionForm
          currentQuestion={currentQuestion}
          addOption={addOption}
          removeOption={removeOption}
          updateOption={updateOption}
        />
      ) : (
        <OpenEndedQuestionForm
          currentQuestion={currentQuestion}
          updateOpenEndedAnswer={updateOpenEndedAnswer}
          addExpectedAnswer={addExpectedAnswer}
          updateExpectedAnswer={updateExpectedAnswer}
          removeExpectedAnswer={removeExpectedAnswer}
        />
      )}

      {/* Explanation */}
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">
          Explanation (Optional)
          <span className="text-xs text-blue-600 ml-2">(Math supported)</span>
        </label>
        <textarea
          value={currentQuestion.explanation}
          onChange={(e) => setCurrentQuestion({ ...currentQuestion, explanation: e.target.value })}
          className="w-full p-3 border border-gray-300 rounded-lg text-sm"
          rows="2"
          placeholder="Explain the answer or provide additional context"
        />
      </div>

      <button
        onClick={addQuestion}
        className="w-full sm:w-auto bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
      >
        ➕ Add Question
      </button>

      {/* Image Crop Modal */}
      {showCropModal && tempImageSrc && (
        <ImageCropModal
          imageSrc={tempImageSrc}
          onCropComplete={handleCropComplete}
          onClose={() => {
            setShowCropModal(false);
            setTempImageSrc(null);
          }}
        />
      )}
    </div>
  );
}

function MultipleChoiceQuestionForm({ currentQuestion, addOption, removeOption, updateOption }) {
  const handleOptionChange = (index, value) => {
    updateOption(index, 'text', value);
    // Trigger MathJax re-render after a short delay
    setTimeout(() => {
      if (window.MathJax) {
        window.MathJax.typesetPromise().catch((err) => console.log('MathJax error:', err));
      }
    }, 300);
  };

  return (
    <div className="mb-4">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-2">
        <label className="block text-gray-700 font-semibold mb-2 sm:mb-0">
          Options *
          <span className="text-xs text-blue-600 ml-2">(Math supported)</span>
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={addOption}
            disabled={currentQuestion.options.length >= 6}
            className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50"
          >
            ➕ Add Option
          </button>
        </div>
      </div>
      
      <div className="space-y-3">
        {currentQuestion.options.map((option, index) => (
          <div key={index} className="border rounded-lg p-3 bg-white">
            <div className="flex items-center gap-2 mb-2">
              <input
                type={currentQuestion.multiple_correct ? 'checkbox' : 'radio'}
                name="correct-answer"
                checked={option.is_correct}
                onChange={(e) => updateOption(index, 'is_correct', e.target.checked)}
              />
              <span className="text-sm font-medium w-6">{String.fromCharCode(65 + index)}.</span>
              <input
                type="text"
                value={option.text}
                onChange={(e) => handleOptionChange(index, e.target.value)}
                className="flex-1 p-2 border border-gray-300 rounded-lg text-sm"
                placeholder={`Option ${String.fromCharCode(65 + index)} (e.g., $x^2$ or regular text)`}
              />
              {currentQuestion.options.length > 2 && (
                <button
                  type="button"
                  onClick={() => removeOption(index)}
                  className="px-2 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                >
                  ✕
                </button>
              )}
            </div>
            
            {/* Math Preview for Options */}
            {option.text && (
              <div className="ml-8 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                <span className="text-xs text-gray-500">Preview: </span>
                <span className="tex2jax_process">{renderMathContent(option.text)}</span>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <p className="text-xs text-gray-500 mt-2">
        {currentQuestion.multiple_correct 
          ? 'Check all correct answers' 
          : 'Select one correct answer'
        } (2-6 options allowed)
      </p>
    </div>
  );
}

function OpenEndedQuestionForm({
  currentQuestion,
  updateOpenEndedAnswer,
  addExpectedAnswer,
  updateExpectedAnswer,
  removeExpectedAnswer
}) {
  return (
    <div className="space-y-4 mb-4">
      {/* Expected Answers */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="block text-gray-700 font-semibold">Expected Answers *</label>
          <button
            type="button"
            onClick={addExpectedAnswer}
            className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
          >
            ➕ Add Answer
          </button>
        </div>
        
        <div className="space-y-2">
          {currentQuestion.open_ended_answer.expected_answers.map((answer, index) => (
            <div key={index} className="flex items-center gap-2">
              <span className="text-sm font-medium w-8">{index + 1}.</span>
              <input
                type="text"
                value={answer}
                onChange={(e) => updateExpectedAnswer(index, e.target.value)}
                className="flex-1 p-2 border border-gray-300 rounded-lg"
                placeholder={`Expected answer ${index + 1}`}
              />
              {currentQuestion.open_ended_answer.expected_answers.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeExpectedAnswer(index)}
                  className="px-2 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Keywords for Auto-grading */}
      <div>
        <label className="block text-gray-700 font-semibold mb-2">Keywords for Partial Credit</label>
        <input
          type="text"
          value={currentQuestion.open_ended_answer.keywords.join(', ')}
          onChange={(e) => updateOpenEndedAnswer('keywords', e.target.value.split(',').map(k => k.trim()).filter(k => k))}
          className="w-full p-2 border border-gray-300 rounded-lg"
          placeholder="Enter keywords separated by commas (optional)"
        />
        <p className="text-xs text-gray-500 mt-1">Keywords found in answers will give partial credit</p>
      </div>

      {/* Grading Options */}
      <div className="flex gap-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={currentQuestion.open_ended_answer.case_sensitive}
            onChange={(e) => updateOpenEndedAnswer('case_sensitive', e.target.checked)}
            className="mr-2"
          />
          <span className="text-sm">Case Sensitive</span>
        </label>
        
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={currentQuestion.open_ended_answer.partial_credit}
            onChange={(e) => updateOpenEndedAnswer('partial_credit', e.target.checked)}
            className="mr-2"
          />
          <span className="text-sm">Allow Partial Credit</span>
        </label>
      </div>
    </div>
  );
}

function QuestionPreview({ question, index, onDelete }) {
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white border rounded-lg p-4">
      <div className="flex justify-between items-start mb-3">
        <h4 className="font-semibold text-gray-800">
          Question {index + 1}: {renderMathContent(question.question_text)}
        </h4>
        <div className="flex gap-2 items-center">
          <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(question.difficulty)}`}>
            {question.difficulty}
          </span>
          <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
            {question.points} pts
          </span>
          {!question.is_mandatory && (
            <span className="px-2 py-1 rounded text-xs bg-gray-100 text-gray-800">
              Optional
            </span>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(index)}
              className="px-2 py-1 rounded text-xs bg-red-600 text-white hover:bg-red-700 transition duration-200"
              title="Remove Question"
            >
              🗑️ Remove
            </button>
          )}
        </div>
      </div>

      {/* Media Display */}
      <div className="flex gap-4 mb-3">
        {question.image_url && (
          <img
            src={question.image_url}
            alt="Question"
            className="w-32 h-20 object-cover rounded"
          />
        )}
        {question.pdf_url && (
          <div className="flex items-center p-2 bg-red-50 rounded">
            <span className="text-red-600">📄 PDF Attached</span>
          </div>
        )}
      </div>

      {/* Question Content */}
      {question.question_type === 'multiple_choice' ? (
        <div>
          <div className="grid grid-cols-2 gap-2 mb-2">
            {question.options.map((option, optIndex) => (
              <div
                key={optIndex}
                className={`p-2 rounded text-sm ${
                  option.is_correct ? 'bg-green-100 text-green-800' : 'bg-gray-100'
                }`}
              >
                {String.fromCharCode(65 + optIndex)}. {renderMathContent(option.text)}
                {option.is_correct && ' ✓'}
              </div>
            ))}
          </div>
          {question.multiple_correct && (
            <p className="text-xs text-blue-600">Multiple correct answers allowed</p>
          )}
        </div>
      ) : (
        <div className="bg-yellow-50 p-3 rounded">
          <p className="text-sm font-medium text-yellow-800 mb-2">Open-ended Question</p>
          <p className="text-xs text-yellow-700">
            Expected: {question.open_ended_answer.expected_answers.join(' OR ')}
          </p>
          {question.open_ended_answer.keywords.length > 0 && (
            <p className="text-xs text-yellow-700">
              Keywords: {question.open_ended_answer.keywords.join(', ')}
            </p>
          )}
        </div>
      )}

      {question.explanation && (
        <div className="mt-3 p-2 bg-blue-50 rounded">
          <p className="text-xs text-blue-700">
            <strong>Explanation:</strong> {question.explanation}
          </p>
        </div>
      )}
    </div>
  );
}

function PasswordChangeModal({ onClose, userName }) {
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.new_password !== formData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    if (formData.new_password.length < 6) {
      setError('New password must be at least 6 characters long');
      return;
    }

    try {
      setLoading(true);
      await apiCall('/auth/change-password', {
        method: 'POST',
        data: {
          current_password: formData.current_password,
          new_password: formData.new_password
        }
      });
      alert('Password changed successfully!');
      onClose();
    } catch (error) {
      setError(error.response?.data?.detail || 'Error changing password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Şifrəni dəyiş</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Köhnə şifrən</label>
            <input
              type="password"
              value={formData.current_password}
              onChange={(e) => setFormData({ ...formData, current_password: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Yeni şifrən</label>
            <input
              type="password"
              value={formData.new_password}
              onChange={(e) => setFormData({ ...formData, new_password: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
              required
              minLength="6"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Yeni şifrəni gir </label>
            <input
              type="password"
              value={formData.confirm_password}
              onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
              required
            />
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-100 text-red-700">
              {error}
            </div>
          )}

          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold disabled:opacity-50"
            >
              {loading ? 'Changing...' : 'Şifrəni dəyiş'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
            >
              Geri
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// User Quiz Taking Components
function UserTakeQuiz({ quiz, currentQuestionIndex, setCurrentQuestionIndex, userAnswers, selectAnswer, nextQuestion, submitQuiz, setCurrentView, isSubmittingQuiz, quizError, setQuizError }) {
  const [showFinishModal, setShowFinishModal] = useState(false);
  
  if (!quiz) return null;

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;

  const handleMultipleChoiceSelect = (optionText) => {
    console.log('Question multiple_correct flag:', currentQuestion.multiple_correct);
    console.log('Current answers:', userAnswers[currentQuestionIndex]);
    console.log('Selecting option:', optionText);
    
    if (currentQuestion.multiple_correct) {
      // Handle multiple correct answers
      const currentAnswers = userAnswers[currentQuestionIndex] ? 
        userAnswers[currentQuestionIndex].split(', ').filter(a => a && a.trim() !== '') : [];
      
      console.log('Current parsed answers:', currentAnswers);
      
      if (currentAnswers.includes(optionText)) {
        // Remove if already selected
        const newAnswers = currentAnswers.filter(a => a !== optionText);
        const newAnswerString = newAnswers.join(', ');
        console.log('Removing option, new answers:', newAnswerString);
        selectAnswer(newAnswerString);
      } else {
        // Add to selected answers
        const newAnswers = [...currentAnswers, optionText];
        const newAnswerString = newAnswers.join(', ');
        console.log('Adding option, new answers:', newAnswerString);
        selectAnswer(newAnswerString);
      }
    } else {
      // Single correct answer
      console.log('Single selection mode, selecting:', optionText);
      selectAnswer(optionText);
    }
  };

  const handleOpenEndedInput = (value) => {
    selectAnswer(value);
  };

  const isOptionSelected = (optionText) => {
    const currentAnswer = userAnswers[currentQuestionIndex] || '';
    if (currentQuestion.multiple_correct) {
      const selectedOptions = currentAnswer.split(', ').filter(a => a && a.trim() !== '');
      return selectedOptions.includes(optionText);
    }
    return currentAnswer === optionText;
  };

  const getQuestionTypeIcon = (type) => {
    return type === 'multiple_choice' ? '📝' : '✏️';
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getAnsweredCount = () => {
    return userAnswers.filter(answer => answer && answer.trim() !== '').length;
  };

  const handleFinishQuiz = () => {
    setShowFinishModal(true);
  };

  const confirmFinishQuiz = () => {
    setShowFinishModal(false);
    // Directly call submitQuiz function
    if (typeof submitQuiz === 'function') {
      submitQuiz();
    } else {
      console.error('submitQuiz function not available');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100">
      <div className="container mx-auto px-2 sm:px-4 py-4 sm:py-8">
        <header className="mb-4 sm:mb-8">
          <button
            onClick={() => setCurrentView('home')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 font-semibold text-sm sm:text-base"
          >
            ← Back to Home
          </button>
          <h1 className="text-2xl sm:text-4xl font-bold text-teal-900 mb-2">{renderMathContent(quiz.title)}</h1>
          <p className="text-gray-600 mb-4 text-sm sm:text-base">{renderMathContent(quiz.description)}</p>
          
          <div className="w-full bg-gray-200 rounded-full h-2 sm:h-3 mb-4">
            <div
              className="bg-teal-600 h-2 sm:h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          
          <div className="flex justify-between items-center text-xs sm:text-sm text-gray-600">
            <span>Sual{currentQuestionIndex + 1} / {quiz.questions.length}</span>
            <span>Cavablanan: {getAnsweredCount()}/{quiz.questions.length}</span>
          </div>
        </header>

        {/* Error Display */}
        {quizError && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <span className="text-red-400 text-xl">❌</span>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-sm font-medium text-red-800">Quiz Submission Failed</h3>
                  <p className="mt-1 text-sm text-red-700">{quizError}</p>
                  <div className="mt-3">
                    <button
                      onClick={() => setQuizError(null)}
                      className="bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded text-sm transition duration-200"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-4 sm:p-8">
          {/* Question Header */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3 flex-wrap">
                <span className="text-xl sm:text-2xl">{getQuestionTypeIcon(currentQuestion.question_type)}</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(currentQuestion.difficulty)}`}>
                  {currentQuestion.difficulty}
                </span>
                <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                  {currentQuestion.points} pts
                </span>
                {!currentQuestion.is_mandatory && (
                  <span className="px-2 py-1 rounded text-xs bg-gray-100 text-gray-800">
                    Optional
                  </span>
                )}
              </div>
              <h2 className="text-lg sm:text-2xl font-semibold text-gray-800">
                {renderMathContent(currentQuestion.question_text)}
              </h2>
            </div>
          </div>

          {/* Media Display */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            {currentQuestion.image_url && (
              <div className="mb-4 sm:mb-6">
                <img
                  src={currentQuestion.image_url}
                  alt="Question"
                  className="max-w-full h-auto rounded-lg shadow"
                  style={{ maxHeight: '300px' }}
                />
              </div>
            )}
            {currentQuestion.pdf_url && (
              <div className="mb-4 sm:mb-6">
                <div className="border-2 border-dashed border-red-300 rounded-lg p-4 sm:p-6 text-center bg-red-50">
                  <div className="text-2xl sm:text-4xl mb-2">📄</div>
                  <p className="text-red-700 font-medium text-sm sm:text-base">PDF Attachment Available</p>
                  <a
                    href={currentQuestion.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 px-3 sm:px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition duration-200 text-sm"
                  >
                    View PDF
                  </a>
                </div>
              </div>
            )}
          </div>

          {/* Question Content Based on Type */}
          <div className="mb-6 sm:mb-8">
            {currentQuestion.question_type === 'multiple_choice' ? (
              <div className="space-y-3 sm:space-y-4">
                {currentQuestion.multiple_correct && (
                  <div className="p-3 bg-blue-50 rounded-lg mb-4">
                    <p className="text-blue-800 text-sm font-medium">
                      📌 Multiple answers may be correct. Select all that apply.
                    </p>
                  </div>
                )}
                
                {currentQuestion.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => handleMultipleChoiceSelect(option.text)}
                    className={`w-full p-3 sm:p-4 text-left rounded-lg border-2 transition duration-200 ${
                      isOptionSelected(option.text)
                        ? 'border-teal-500 bg-teal-50 text-teal-800'
                        : 'border-gray-200 hover:border-teal-300 hover:bg-teal-50'
                    }`}
                  >
                    <div className="flex items-center">
                      <div className={`w-4 h-4 mr-3 border-2 rounded ${
                        currentQuestion.multiple_correct ? 'rounded-sm' : 'rounded-full'
                      } ${
                        isOptionSelected(option.text)
                          ? 'bg-teal-500 border-teal-500'
                          : 'border-gray-300'
                      }`}>
                        {isOptionSelected(option.text) && (
                          <div className="text-white text-xs text-center leading-4">
                            {currentQuestion.multiple_correct ? '✓' : '●'}
                          </div>
                        )}
                      </div>
                      <span className="font-semibold mr-3 text-sm sm:text-base">{String.fromCharCode(65 + index)}.</span>
                      <span className="flex-1 text-sm sm:text-base">{renderMathContent(option.text)}</span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-3 bg-yellow-50 rounded-lg mb-4">
                  <p className="text-yellow-800 text-sm font-medium">
                    ✏️ Açıq sual. Cavabınızı aşağıdakı mətn sahəsində yazın.
                  </p>
                </div>
                
                <textarea
                  value={userAnswers[currentQuestionIndex] || ''}
                  onChange={(e) => handleOpenEndedInput(e.target.value)}
                  className="w-full p-3 sm:p-4 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:outline-none resize-y min-h-24 sm:min-h-32 text-sm sm:text-base"
                  placeholder="Type your answer here..."
                  rows="4"
                />
                
                <div className="text-xs sm:text-sm text-gray-500">
                  {userAnswers[currentQuestionIndex]?.length || 0} Simvol
                </div>
              </div>
            )}
          </div>

          {/* Navigation Buttons */}
          <div className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-0">
            <button
              onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
              disabled={currentQuestionIndex === 0}
              className="px-4 sm:px-6 py-2 sm:py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
            >
              Geri
            </button>
            
            <div className="flex gap-2 sm:gap-3">
              <button
                onClick={handleFinishQuiz}
                className="px-3 sm:px-4 py-2 sm:py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition duration-200 font-semibold text-xs sm:text-sm"
              >
                🏁 Sınağı bitir
              </button>
              
              <button
                onClick={nextQuestion}
                disabled={!userAnswers[currentQuestionIndex] || 
                         (userAnswers[currentQuestionIndex] && userAnswers[currentQuestionIndex].trim() === '')}
                className="px-4 sm:px-6 py-2 sm:py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-sm sm:text-base"
              >
                {currentQuestionIndex === quiz.questions.length - 1 ? 'sınaq bitsin' : 'Növbəti Sual'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Finish Quiz Confirmation Modal */}
      {showFinishModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">🏁</div>
              <h3 className="text-lg font-semibold mb-2">Sınağı bitir</h3>
              <p className="text-gray-600 text-sm">
               Cavabladığınız suallar{getAnsweredCount()}/{quiz.questions.length} 
              </p>
              {getAnsweredCount() < quiz.questions.length && (
                <p className="text-orange-600 text-sm mt-2">
                  ⚠️ {quiz.questions.length - getAnsweredCount()} Suallar cavabsız qeyd ediləcək.
                </p>
              )}
            </div>

            <div className="flex gap-4">
              <button
                onClick={confirmFinishQuiz}
                disabled={isSubmittingQuiz}
                className={`flex-1 py-3 rounded-lg font-semibold transition duration-200 ${
                  isSubmittingQuiz 
                    ? 'bg-gray-400 text-gray-700 cursor-not-allowed' 
                    : 'bg-orange-600 text-white hover:bg-orange-700'
                }`}
              >
                {isSubmittingQuiz ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                   Göndərilir...
                  </div>
                ) : (
                  'sınağı bitir'
                )}
              </button>
              <button
                onClick={() => setShowFinishModal(false)}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
              >
                Sınağa davam et
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Real-time Quiz Session Component with Timer
function RealTimeQuizSession({ quiz, setCurrentView, user, setQuizResult, setIsTimedQuiz }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [showFinishModal, setShowFinishModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sessionStatus, setSessionStatus] = useState('pending'); // pending, active, paused, completed, expired
  const [autoSubmitWarning, setAutoSubmitWarning] = useState(false);
  
  // Timer ref for cleanup
  const timerRef = useRef(null);

  // Start new quiz session
  const startSession = async (customTimeLimit = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/quiz-session/start`,
        {
          quiz_id: quiz.id,
          time_limit_minutes: customTimeLimit
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      const newSession = response.data;
      setSession(newSession);
      setUserAnswers(new Array(newSession.total_questions).fill(''));
      setTimeRemaining(newSession.time_remaining_seconds);
      setSessionStatus(newSession.status);
      
      // Automatically activate session
      if (newSession.status === 'pending') {
        await activateSession(newSession.id);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to start quiz session');
    } finally {
      setLoading(false);
    }
  };

  // Activate pending session (start timer)
  const activateSession = async (sessionId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/quiz-session/${sessionId}/activate`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      const activatedSession = response.data;
      setSession(activatedSession);
      setSessionStatus(activatedSession.status);
      setTimeRemaining(activatedSession.time_remaining_seconds);
      
      // Start timer
      if (activatedSession.time_remaining_seconds) {
        startTimer();
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to activate session');
    }
  };

  // Start countdown timer
  const startTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          // Time expired - auto submit
          clearInterval(timerRef.current);
          setSessionStatus('expired');
          setAutoSubmitWarning(true);
          autoSubmitQuiz();
          return 0;
        }
        
        // Show warning when 5 minutes or 10% time remaining (whichever is less)
        const warningThreshold = Math.min(300, session?.time_remaining_seconds * 0.1);
        if (prev <= warningThreshold && prev > warningThreshold - 1) {
          setAutoSubmitWarning(true);
        }
        
        return prev - 1;
      });
    }, 1000);
  };

  // Update session progress
  const updateSession = async (updates) => {
    if (!session) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API}/quiz-session/${session.id}/update`,
        updates,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
    } catch (error) {
      console.error('Failed to update session:', error);
    }
  };

  // Handle answer selection
  const selectAnswer = (answer) => {
    const newAnswers = [...userAnswers];
    newAnswers[currentQuestionIndex] = answer;
    setUserAnswers(newAnswers);
    
    // Update session with current progress
    updateSession({
      current_question_index: currentQuestionIndex,
      answers: newAnswers
    });
  };

  // Move to next question
  const nextQuestion = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      const newIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(newIndex);
      updateSession({
        current_question_index: newIndex,
        answers: userAnswers
      });
    } else {
      // Last question - show finish modal
      setShowFinishModal(true);
    }
  };

  // Auto-submit when time expires
  const autoSubmitQuiz = async () => {
    await submitQuizSession(true);
  };

  // Submit quiz session
  const submitQuizSession = async (isAutoSubmit = false) => {
    if (!session) return;
    
    setIsSubmitting(true);
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/quiz-session/${session.id}/submit`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      const result = response.data;
      
      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      
      // Set the quiz result data for the parent component
      if (setQuizResult) {
        setQuizResult(result);
      }
      
      // Mark this as a timed quiz for proper display
      if (setIsTimedQuiz) {
        setIsTimedQuiz(true);
      }
      
      // Navigate to results
      setCurrentView('result');
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit quiz');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Pause session
  const pauseSession = async () => {
    if (!session) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.get(
        `${API}/quiz-session/${session.id}/pause`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setSessionStatus('paused');
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to pause session');
    }
  };

  // Resume session
  const resumeSession = async () => {
    if (!session) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.get(
        `${API}/quiz-session/${session.id}/resume`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setSessionStatus('active');
      if (timeRemaining > 0) {
        startTimer();
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to resume session');
    }
  };

  // Format time display
  const formatTime = (seconds) => {
    if (!seconds) return '--:--';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  // Get timer color based on remaining time
  const getTimerColor = () => {
    if (!timeRemaining || !session?.time_remaining_seconds) return 'text-green-600';
    
    const percentage = (timeRemaining / session.time_remaining_seconds) * 100;
    
    if (percentage <= 10) return 'text-red-600 animate-pulse';
    if (percentage <= 25) return 'text-orange-600';
    if (percentage <= 50) return 'text-yellow-600';
    return 'text-green-600';
  };

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Session not started - show start screen
  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          <button
            onClick={() => setCurrentView('home')}
            className="mb-6 text-indigo-600 hover:text-indigo-800 font-semibold"
          >
            ← Sınaqlara geri dön
          </button>
          
          <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">⏱️</div>
              <h1 className="text-3xl font-bold text-gray-800 mb-4">Canlı Sual-Cavab</h1>
              <h2 className="text-xl font-semibold text-indigo-600 mb-2">{quiz.title}</h2>
              <p className="text-gray-600 mb-6">{quiz.description}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl mb-2">📝</div>
                <h3 className="font-semibold text-blue-800">Suallar</h3>
                <p className="text-blue-600">{quiz.questions.length} suallar</p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl mb-2">⭐</div>
                <h3 className="font-semibold text-green-800">Xal</h3>
                <p className="text-green-600">{quiz.total_points} ümumi xal</p>
              </div>
              
              {quiz.time_limit_minutes && (
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-2xl mb-2">⏰</div>
                  <h3 className="font-semibold text-orange-800">Vaxt limiti</h3>
                  <p className="text-orange-600">{quiz.time_limit_minutes} dəqiqə</p>
                </div>
              )}
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl mb-2">🎯</div>
                <h3 className="font-semibold text-purple-800">Keçid balı</h3>
                <p className="text-purple-600">{quiz.min_pass_percentage}%</p>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
                <p className="text-red-700">{error}</p>
              </div>
            )}

            <div className="text-center">
              <button
                onClick={() => startSession()}
                disabled={loading}
                className={`px-8 py-3 bg-indigo-600 text-white rounded-lg font-semibold text-lg transition duration-200 ${
                  loading 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'hover:bg-indigo-700 transform hover:scale-105'
                }`}
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Sessiyaya başlanır
                  </div>
                ) : (
                  'Sınağa Başla'
                )}
              </button>
              
              <p className="text-sm text-gray-500 mt-4">
                Timer başlayandan dərhal sonra işə düşəcək
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Session started - show quiz interface
  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100">
      <div className="container mx-auto px-2 sm:px-4 py-4 sm:py-8">
        {/* Header with Timer */}
        <header className="mb-4 sm:mb-8">
          <div className="flex justify-between items-start mb-4">
            <button
              onClick={() => setCurrentView('home')}
              className="text-indigo-600 hover:text-indigo-800 font-semibold text-sm sm:text-base"
            >
              ← Sınaqlara geri dön
            </button>
            
            {/* Timer Display */}
            {timeRemaining !== null && (
              <div className="bg-white rounded-lg shadow-lg p-3 border-l-4 border-indigo-500">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">⏱️</span>
                  <div>
                    <div className={`text-2xl font-bold ${getTimerColor()}`}>
                      {formatTime(timeRemaining)}
                    </div>
                    <div className="text-xs text-gray-500">Qalan vaxt</div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <h1 className="text-2xl sm:text-4xl font-bold text-teal-900 mb-2">{quiz.title}</h1>
          <p className="text-gray-600 mb-4 text-sm sm:text-base">{quiz.description}</p>
          
          {/* Session Status Indicator */}
          <div className="flex items-center space-x-4 mb-4">
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              sessionStatus === 'active' ? 'bg-green-100 text-green-800' :
              sessionStatus === 'paused' ? 'bg-yellow-100 text-yellow-800' :
              sessionStatus === 'expired' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {sessionStatus === 'active' && '🟢 Active'}
              {sessionStatus === 'paused' && '⏸️ Paused'}
              {sessionStatus === 'expired' && '⏰ Expired'}
              {sessionStatus === 'pending' && '⏳ Starting...'}
            </div>
            
            {sessionStatus === 'active' && timeRemaining > 0 && (
              <button
                onClick={pauseSession}
                className="px-3 py-1 bg-yellow-600 text-white rounded text-sm hover:bg-yellow-700 transition"
              >
                ⏸️ Pause
              </button>
            )}
            
            {sessionStatus === 'paused' && (
              <button
                onClick={resumeSession}
                className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 transition"
              >
                ▶️ Resume
              </button>
            )}
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 sm:h-3 mb-4">
            <div
              className="bg-teal-600 h-2 sm:h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          
          <div className="flex justify-between items-center text-xs sm:text-sm text-gray-600">
            <span>Sual {currentQuestionIndex + 1} / {quiz.questions.length}</span>
            <span>Cavablanan: {userAnswers.filter(a => a && a.trim()).length}/{quiz.questions.length}</span>
          </div>
        </header>

        {/* Auto-submit Warning */}
        {autoSubmitWarning && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-orange-50 border-l-4 border-orange-400 p-4 rounded-r-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <span className="text-orange-400 text-xl">⚠️</span>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-sm font-medium text-orange-800">Vaxt bildirişi</h3>
                  <p className="mt-1 text-sm text-orange-700">
                    {timeRemaining <= 60 
                      ? 'Less than 1 minute remaining! Quiz will auto-submit when time expires.'
                      : 'Time is running low. Quiz will auto-submit when timer reaches zero.'
                    }
                  </p>
                  <div className="mt-3">
                    <button
                      onClick={() => setAutoSubmitWarning(false)}
                      className="bg-orange-100 hover:bg-orange-200 text-orange-800 px-3 py-1 rounded text-sm transition duration-200"
                    >
                      Bağla
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <span className="text-red-400 text-xl">❌</span>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-sm font-medium text-red-800">Session Error</h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                  <div className="mt-3">
                    <button
                      onClick={() => setError(null)}
                      className="bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded text-sm transition duration-200"
                    >
                      Bağla
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Question Content - Reuse existing UserTakeQuiz logic */}
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-4 sm:p-8">
          {/* Question Header */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3 flex-wrap">
                <span className="text-xl sm:text-2xl">
                  {currentQuestion.question_type === 'multiple_choice' ? '📝' : '✏️'}
                </span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  currentQuestion.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                  currentQuestion.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  currentQuestion.difficulty === 'hard' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {currentQuestion.difficulty}
                </span>
                <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                  {currentQuestion.points} pts
                </span>
              </div>
              <h2 className="text-lg sm:text-2xl font-semibold text-gray-800">
                {renderMathContent(currentQuestion.question_text)}
              </h2>
            </div>
          </div>

          {/* Media Display */}
          {currentQuestion.image_url && (
            <div className="mb-4 sm:mb-6">
              <img
                src={currentQuestion.image_url}
                alt="Question"
                className="max-w-full h-auto rounded-lg shadow"
                style={{ maxHeight: '300px' }}
              />
            </div>
          )}

          {/* Question Content Based on Type */}
          <div className="mb-6 sm:mb-8">
            {currentQuestion.question_type === 'multiple_choice' ? (
              <div className="space-y-3 sm:space-y-4">
                {currentQuestion.multiple_correct && (
                  <div className="p-3 bg-blue-50 rounded-lg mb-4">
                    <p className="text-blue-800 text-sm font-medium">
                      📌 Birdən çox cavab doğru ola bilər. Uyğun olanların hamısını seçin.
                    </p>
                  </div>
                )}
                
                {currentQuestion.options.map((option, index) => {
                  const isSelected = currentQuestion.multiple_correct
                    ? (userAnswers[currentQuestionIndex] || '').split(', ').includes(option.text)
                    : userAnswers[currentQuestionIndex] === option.text;
                    
                  return (
                    <button
                      key={index}
                      onClick={() => {
                        if (sessionStatus !== 'active') return;
                        
                        if (currentQuestion.multiple_correct) {
                          const currentAnswers = userAnswers[currentQuestionIndex] ? 
                            userAnswers[currentQuestionIndex].split(', ').filter(a => a && a.trim() !== '') : [];
                          
                          if (currentAnswers.includes(option.text)) {
                            const newAnswers = currentAnswers.filter(a => a !== option.text);
                            selectAnswer(newAnswers.join(', '));
                          } else {
                            const newAnswers = [...currentAnswers, option.text];
                            selectAnswer(newAnswers.join(', '));
                          }
                        } else {
                          selectAnswer(option.text);
                        }
                      }}
                      disabled={sessionStatus !== 'active'}
                      className={`w-full p-3 sm:p-4 text-left rounded-lg border-2 transition duration-200 ${
                        sessionStatus !== 'active' ? 'opacity-50 cursor-not-allowed' :
                        isSelected
                          ? 'border-teal-500 bg-teal-50 text-teal-800'
                          : 'border-gray-200 hover:border-teal-300 hover:bg-teal-50'
                      }`}
                    >
                      <div className="flex items-center">
                        <div className={`w-4 h-4 mr-3 border-2 rounded ${
                          currentQuestion.multiple_correct ? 'rounded-sm' : 'rounded-full'
                        } ${
                          isSelected
                            ? 'bg-teal-500 border-teal-500'
                            : 'border-gray-300'
                        }`}>
                          {isSelected && (
                            <div className="text-white text-xs text-center leading-4">
                              {currentQuestion.multiple_correct ? '✓' : '●'}
                            </div>
                          )}
                        </div>
                        <span className="font-semibold mr-3 text-sm sm:text-base">{String.fromCharCode(65 + index)}.</span>
                        <span className="flex-1 text-sm sm:text-base">{renderMathContent(option.text)}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-3 bg-yellow-50 rounded-lg mb-4">
                  <p className="text-yellow-800 text-sm font-medium">
                    ✏️ Açıq sual. Cavabınızı aşağıdakı mətn sahəsində yazın.
                  </p>
                </div>
                
                <textarea
                  value={userAnswers[currentQuestionIndex] || ''}
                  onChange={(e) => sessionStatus === 'active' && selectAnswer(e.target.value)}
                  disabled={sessionStatus !== 'active'}
                  className={`w-full p-3 sm:p-4 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:outline-none resize-y min-h-24 sm:min-h-32 text-sm sm:text-base ${
                    sessionStatus !== 'active' ? 'opacity-50 bg-gray-100 cursor-not-allowed' : ''
                  }`}
                  placeholder={sessionStatus === 'active' ? "Type your answer here..." : "Session paused - resume to continue"}
                  rows="4"
                />
                
                <div className="text-xs sm:text-sm text-gray-500">
                  {userAnswers[currentQuestionIndex]?.length || 0} simvollar
                </div>
              </div>
            )}
          </div>

          {/* Navigation Buttons */}
          <div className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-0">
            <button
              onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
              disabled={currentQuestionIndex === 0 || sessionStatus !== 'active'}
              className="px-4 sm:px-6 py-2 sm:py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
            >
              Geri
            </button>
            
            <div className="flex gap-2 sm:gap-3">
              <button
                onClick={() => setShowFinishModal(true)}
                disabled={sessionStatus !== 'active' && sessionStatus !== 'expired'}
                className="px-3 sm:px-4 py-2 sm:py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition duration-200 font-semibold text-xs sm:text-sm disabled:opacity-50"
              >
                🏁 Sınağı bitir
              </button>
              
              <button
                onClick={nextQuestion}
                disabled={sessionStatus !== 'active' || !userAnswers[currentQuestionIndex] || 
                         (userAnswers[currentQuestionIndex] && userAnswers[currentQuestionIndex].trim() === '')}
                className="px-4 sm:px-6 py-2 sm:py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-sm sm:text-base"
              >
                {currentQuestionIndex === quiz.questions.length - 1 ? 'sınaq bitsin' : 'Növbəti Sual'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Finish Quiz Confirmation Modal */}
      {showFinishModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">
                {sessionStatus === 'expired' ? '⏰' : '🏁'}
              </div>
              <h3 className="text-lg font-semibold mb-2">
                {sessionStatus === 'expired' ? 'Time Expired!' : 'Sınaq Bitsin?'}
              </h3>
              <p className="text-gray-600 text-sm">
                Sənin nəticən {userAnswers.filter(a => a && a.trim()).length}/{quiz.questions.length} 
              </p>
              {sessionStatus === 'expired' && (
                <p className="text-red-600 text-sm mt-2">
                  ⏰ Vaxt bitdi! Sınaq avtomatik olaraq göndəriləcək.
                </p>
              )}
              {userAnswers.filter(a => a && a.trim()).length < quiz.questions.length && sessionStatus !== 'expired' && (
                <p className="text-orange-600 text-sm mt-2">
                  ⚠️ {quiz.questions.length - userAnswers.filter(a => a && a.trim()).length} suallar cavabsız qalacaq.
                </p>
              )}
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => submitQuizSession(sessionStatus === 'expired')}
                disabled={isSubmitting}
                className={`flex-1 py-3 rounded-lg font-semibold transition duration-200 ${
                  isSubmitting 
                    ? 'bg-gray-400 text-gray-700 cursor-not-allowed' 
                    : sessionStatus === 'expired'
                      ? 'bg-red-600 text-white hover:bg-red-700'
                      : 'bg-orange-600 text-white hover:bg-orange-700'
                }`}
              >
                {isSubmitting ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </div>
                ) : sessionStatus === 'expired' ? (
                  'Sınaq bitsin'
                ) : (
                  'Bəli, sınağı bitir'
                )}
              </button>
              
              {sessionStatus !== 'expired' && (
                <button
                  onClick={() => setShowFinishModal(false)}
                  className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
                >
                  Sınağa davam et
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function UserResult({ result, quiz, setCurrentView, startQuiz, startRealTimeQuiz, isTimedQuiz }) {
  const [detailedResults, setDetailedResults] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [showMistakes, setShowMistakes] = useState(false);

  useEffect(() => {
    if (result && result.question_results) {
      setDetailedResults(result.question_results);
    }
    fetchLeaderboard();
  }, [result, quiz]);

  const fetchLeaderboard = async () => {
    try {
      const response = await apiCall(`/quiz/${quiz.id}/results-ranking`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  if (!result) return null;

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceBadge = (percentage) => {
    if (percentage >= 80) return { text: 'Əla!', color: 'bg-green-500' };
    if (percentage >= 60) return { text: 'Yaxşı!', color: 'bg-yellow-500' };
    return { text: 'Cəhd etməyə davam et!', color: 'bg-red-500' };
  };

  const badge = getPerformanceBadge(result.percentage);
  const mistakes = detailedResults ? detailedResults.filter(q => !q.is_correct) : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Main Result Card */}
          <div className="bg-white rounded-lg shadow-lg p-8 text-center mb-6">
            <div className="mb-8">
              <div className={`inline-block px-4 py-2 rounded-full text-white text-sm font-semibold mb-4 ${badge.color}`}>
                {badge.text}
              </div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">Sınaq tamamlandı!</h1>
              <h2 className="text-2xl font-semibold text-gray-700 mb-6">{quiz.title}</h2>
            </div>

            {/* Score Display */}
            <div className="mb-8">
              <div className="text-6xl font-bold mb-4">
                <span className={getScoreColor(result.percentage)}>
                  {result.percentage.toFixed(1)}%
                </span>
              </div>
              <p className="text-xl text-gray-600 mb-2">
                Sənin düzgün cavabların {result.score}/{result.total_questions}
              </p>
              <div className="w-full bg-gray-200 rounded-full h-4 mb-4 max-w-md mx-auto">
                <div
                  className={`h-4 rounded-full transition-all duration-1000 ${
                    result.percentage >= 80 ? 'bg-green-500' :
                    result.percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${result.percentage}%` }}
                ></div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <button
                onClick={() => setCurrentView('home')}
                className="bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold"
              >
                🏠 Sınaqlara qayıt
              </button>
              <button
                onClick={() => isTimedQuiz ? startRealTimeQuiz(quiz) : startQuiz(quiz)}
                className="bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
              >
                🔄 Yenidən işlə
              </button>
              <button
                onClick={() => setShowMistakes(!showMistakes)}
                className="bg-orange-600 text-white py-3 rounded-lg hover:bg-orange-700 transition duration-200 font-semibold"
              >
                {showMistakes ? '👁️ Baxışı gizlət' : '📝 Səhvlərinə bax'}
              </button>
            </div>
          </div>

          {/* Mistakes Review */}
          {showMistakes && detailedResults && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h3 className="text-2xl font-semibold text-gray-800 mb-6">📝 Ətraflı baxış</h3>
              
              <div className="space-y-4">
                {detailedResults.map((questionResult, index) => (
                  <div
                    key={index}
                    className={`border rounded-lg p-4 ${
                      questionResult.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-semibold text-gray-800">
                        Question {questionResult.question_number}: {questionResult.question_text}
                      </h4>
                      <span className={`px-2 py-1 rounded text-sm font-semibold ${
                        questionResult.is_correct 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {questionResult.is_correct ? '✅ Düz' : '❌ Səhv'}
                      </span>
                    </div>

                    {questionResult.question_image && (
                      <img
                        src={questionResult.question_image}
                        alt="Question"
                        className="max-w-xs h-auto rounded-lg shadow mb-3"
                      />
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-semibold text-gray-600 mb-2">Sənin cavabın:</p>
                        <p className={`p-2 rounded ${
                          questionResult.is_correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {questionResult.user_answer}
                        </p>
                      </div>
                      
                      {!questionResult.is_correct && (
                        <div>
                          <p className="text-sm font-semibold text-gray-600 mb-2">Düzgün cavab:</p>
                          <p className="p-2 rounded bg-green-100 text-green-800">
                            {questionResult.correct_answer}
                          </p>
                        </div>
                      )}
                    </div>

                    {!questionResult.is_correct && (
                      <div className="mt-3">
                        <p className="text-sm font-semibold text-gray-600 mb-2">Variantlar:</p>
                        <div className="grid grid-cols-2 gap-2">
                          {questionResult.all_options.map((option, optIndex) => (
                            <div
                              key={optIndex}
                              className={`p-2 rounded text-sm ${
                                option === questionResult.correct_answer
                                  ? 'bg-green-100 text-green-800 border-2 border-green-300'
                                  : option === questionResult.user_answer
                                  ? 'bg-red-100 text-red-800 border-2 border-red-300'
                                  : 'bg-gray-100 text-gray-700'
                              }`}
                            >
                              {String.fromCharCode(65 + optIndex)}. {option}
                              {option === questionResult.correct_answer && ' ✓'}
                              {option === questionResult.user_answer && option !== questionResult.correct_answer && ' ✗'}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">Yekun:</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-green-600 font-semibold">Düzgün: </span>
                    {detailedResults.filter(q => q.is_correct).length} Suallar
                  </div>
                  <div>
                    <span className="text-red-600 font-semibold">Səhv: </span>
                    {mistakes.length} questions
                  </div>
                  <div>
                    <span className="text-blue-600 font-semibold">Boş: </span>
                    {result.percentage.toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Leaderboard */}
          {leaderboard && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-2xl font-semibold text-gray-800 mb-6">🏆 Yüksək nəticələr</h3>
              
              {/* Top 3 */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-700 mb-4">Top 3 nəticə</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {leaderboard.top_3.map((entry, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg text-center ${
                        index === 0 ? 'bg-yellow-100 border-2 border-yellow-300' :
                        index === 1 ? 'bg-gray-100 border-2 border-gray-300' :
                        'bg-orange-100 border-2 border-orange-300'
                      }`}
                    >
                      <div className="text-2xl mb-2">
                        {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                      </div>
                      <p className="font-semibold text-gray-800">{entry.user_name}</p>
                      <p className="text-lg font-bold text-gray-900">{entry.percentage.toFixed(1)}%</p>
                      <p className="text-sm text-gray-600">
                        {entry.score}/{entry.total_questions} Doğru
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* User's Position */}
              {leaderboard.user_position && (
                <div className="mb-6 p-4 bg-indigo-50 rounded-lg">
                  <h4 className="text-lg font-semibold text-indigo-800 mb-2">Sənin Sıran</h4>
                  <p className="text-indigo-700">
                    Sənin nəticən <span className="font-bold">#{leaderboard.user_position.rank}</span> {' '}
                    <span className="font-bold">{leaderboard.total_participants}</span> 
                  </p>
                </div>
              )}

              {/* Quiz Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-800">{leaderboard.total_participants}</p>
                  <p className="text-sm text-gray-600">Cəmi iştirakçılar</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-800">{leaderboard.quiz_stats.total_attempts}</p>
                  <p className="text-sm text-gray-600">Ümumi cəhdlər</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-800">{leaderboard.quiz_stats.average_score.toFixed(1)}%</p>
                  <p className="text-sm text-gray-600">Orta nəticə</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Quiz Card Component
function QuizCard({ quiz, startQuiz, startRealTimeQuiz, currentUser }) {
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [bookmarking, setBookmarking] = useState(false);

  // Check bookmark status when component mounts
  useEffect(() => {
    if (currentUser) {
      checkBookmarkStatus();
    }
  }, [quiz.id, currentUser]);

  const checkBookmarkStatus = async () => {
    try {
      const response = await apiCall(`/bookmarks/check/${quiz.id}?item_type=quiz`);
      setIsBookmarked(response.data.is_bookmarked);
    } catch (error) {
      console.error('Error checking bookmark status:', error);
    }
  };

  const handleBookmark = async (e) => {
    e.stopPropagation();
    if (bookmarking || !currentUser) return;
    
    setBookmarking(true);
    try {
      if (isBookmarked) {
        await apiCall(`/bookmarks/${quiz.id}?item_type=quiz`, { method: 'DELETE' });
        setIsBookmarked(false);
      } else {
        await apiCall('/bookmarks', {
          method: 'POST',
          data: { item_id: quiz.id, item_type: 'quiz' }
        });
        setIsBookmarked(true);
      }
    } catch (error) {
      console.error('Error toggling bookmark:', error);
      alert('Failed to bookmark: ' + (error.response?.data?.detail || 'Unknown error'));
    }
    setBookmarking(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xl font-semibold text-gray-800 flex-1 mr-2">{quiz.title}</h3>
        {currentUser && (
          <button
            onClick={handleBookmark}
            disabled={bookmarking}
            className={`p-2 rounded-full transition duration-200 ${
              isBookmarked
                ? 'text-blue-600 bg-blue-50 hover:bg-blue-100'
                : 'text-gray-400 hover:text-blue-600 hover:bg-blue-50'
            } ${bookmarking ? 'opacity-50 cursor-not-allowed' : ''}`}
            title={isBookmarked ? 'Remove bookmark' : 'Bookmark quiz'}
          >
            {isBookmarked ? '🔖' : '📄'}
          </button>
        )}
      </div>
      <p className="text-gray-600 mb-4">{quiz.description}</p>
      <div className="flex justify-between items-center mb-4 text-sm text-gray-500">
        <span>{quiz.total_questions} suallar</span>
        <span>{quiz.total_attempts || 0} cəhdlər</span>
      </div>
      <div className="flex justify-between items-center mb-4">
        <span className="text-sm text-gray-500">
         Cateqoriya: {quiz.category}
        </span>
        <span className="text-sm text-gray-500">
          faiz: {quiz.average_score || 0}%
        </span>
      </div>
      <div className="flex gap-2">
        {quiz.time_limit_minutes ? (
          // Time limit is set → Only show Timed mode
          <button
            onClick={() => startRealTimeQuiz(quiz)}
            className="flex-1 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold text-sm"
          >
            ⏱️ Başla (Zamanlı)
          </button>
        ) : (
          // No time limit → Only show Standard mode
          <button
            onClick={() => startQuiz(quiz)}
            className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition duration-200 font-semibold text-sm"
          >
            📝 Başla
          </button>
        )}
      </div>
      {quiz.time_limit_minutes && (
        <div className="mt-2 text-xs text-gray-500 text-center">
          ⏰ {quiz.time_limit_minutes} Dəqiqə limit
        </div>
      )}
    </div>
  );
}

// User Home Component with Hierarchical Subject/Subcategory Structure
function UserHome({ quizzes, startQuiz, startRealTimeQuiz, currentUser }) {
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedSubcategory, setSelectedSubcategory] = useState(null);

  // Group quizzes by subject and subcategory
  const groupedQuizzes = quizzes.reduce((acc, quiz) => {
    const subject = quiz.subject || 'General';
    const subcategory = quiz.subcategory || 'General';
    
    if (!acc[subject]) {
      acc[subject] = {};
    }
    if (!acc[subject][subcategory]) {
      acc[subject][subcategory] = [];
    }
    acc[subject][subcategory].push(quiz);
    return acc;
  }, {});

  const subjects = Object.keys(groupedQuizzes).sort();

  // Reset selection when going back
  const handleBackToSubjects = () => {
    setSelectedSubject(null);
    setSelectedSubcategory(null);
  };

  const handleBackToSubcategories = () => {
    setSelectedSubcategory(null);
  };

  // Custom CSS button styling
  const CategoryButton = ({ children, onClick, icon = "" }) => (
    <button 
      onClick={onClick}
      className="cssbuttons-io"
      style={{
        position: 'relative',
        fontFamily: 'inherit',
        fontWeight: 500,
        fontSize: '18px',
        letterSpacing: '0.05em',
        borderRadius: '0.8em',
        cursor: 'pointer',
        border: 'none',
        background: 'linear-gradient(to right, #8e2de2, #4a00e0)',
        color: 'ghostwhite',
        overflow: 'hidden',
        margin: '0.5rem',
        transition: 'transform 0.2s'
      }}
      onMouseEnter={(e) => {
        e.target.style.transform = 'scale(1.02)';
      }}
      onMouseLeave={(e) => {
        e.target.style.transform = 'scale(1)';
      }}
      onMouseDown={(e) => {
        e.target.style.transform = 'scale(0.95)';
      }}
      onMouseUp={(e) => {
        e.target.style.transform = 'scale(1.02)';
      }}
    >
      <span style={{
        position: 'relative',
        zIndex: 10,
        transition: 'color 0.4s',
        display: 'inline-flex',
        alignItems: 'center',
        padding: '0.8em 1.2em 0.8em 1.05em'
      }}>
        {icon && <span style={{ marginRight: '0.5em' }}>{icon}</span>}
        {children}
      </span>
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        content: '""',
        background: '#000',
        width: '120%',
        left: '-10%',
        transform: 'skew(30deg)',
        transition: 'transform 0.4s cubic-bezier(0.3, 1, 0.8, 1)'
      }} />
    </button>
  );

  if (quizzes.length === 0) {
    return (
      <div>
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Available Quizzes</h2>
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No quizzes available yet.</p>
        </div>
      </div>
    );
  }

  // Show quiz list when subcategory is selected
  if (selectedSubject && selectedSubcategory) {
    const subcategoryQuizzes = groupedQuizzes[selectedSubject][selectedSubcategory];
    return (
      <div>
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-4">
            <CategoryButton onClick={handleBackToSubjects} icon="🏠">
              Bütün Mövzular
            </CategoryButton>
            <span className="text-gray-500">→</span>
            <CategoryButton onClick={handleBackToSubcategories} icon="📚">
              {selectedSubject}
            </CategoryButton>
            <span className="text-gray-500">→</span>
            <span className="text-lg font-semibold text-gray-800">📂 {selectedSubcategory}</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-800">
            {selectedSubject} - {selectedSubcategory} Sınaqlar
          </h2>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {subcategoryQuizzes.map((quiz) => (
            <QuizCard 
              key={quiz.id} 
              quiz={quiz} 
              startQuiz={startQuiz}
              startRealTimeQuiz={startRealTimeQuiz}
              currentUser={currentUser}
            />
          ))}
        </div>
      </div>
    );
  }

  // Show subcategories when subject is selected
  if (selectedSubject) {
    const subcategories = Object.keys(groupedQuizzes[selectedSubject]).sort();
    return (
      <div>
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-4">
            <CategoryButton onClick={handleBackToSubjects} icon="🏠">
              B
            </CategoryButton>
            <span className="text-gray-500">→</span>
            <span className="text-lg font-semibold text-gray-800">📚 {selectedSubject}</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-800">
            {selectedSubject} Bölmələr
          </h2>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {subcategories.map((subcategory) => {
            const quizCount = groupedQuizzes[selectedSubject][subcategory].length;
            return (
              <div
                key={subcategory}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200"
              >
                <div className="text-center">
                  <div className="text-4xl mb-3">📂</div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">{subcategory}</h3>
                  <p className="text-gray-500 mb-4">{quizCount} sınaq{quizCount !== 1 ? 'lar' : ''}</p>
                  <CategoryButton 
                    onClick={() => setSelectedSubcategory(subcategory)}
                    icon="📖"
                  >
                    Sınaqları Göstər
                  </CategoryButton>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Show subjects (main view)
  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-800 mb-6">📚 Test mövzuları</h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {subjects.map((subject) => {
          const subcategoryCount = Object.keys(groupedQuizzes[subject]).length;
          const totalQuizCount = Object.values(groupedQuizzes[subject])
            .reduce((total, quizzes) => total + quizzes.length, 0);
          
          // Get subject icon
          const getSubjectIcon = (subjectName) => {
            const subjectLower = subjectName.toLowerCase();
            if (subjectLower.includes('math')) return '🔢';
            if (subjectLower.includes('science')) return '🔬';
            if (subjectLower.includes('physics')) return '⚛️';
            if (subjectLower.includes('chemistry')) return '🧪';
            if (subjectLower.includes('biology')) return '🧬';
            if (subjectLower.includes('history')) return '📜';
            if (subjectLower.includes('english') || subjectLower.includes('language')) return '📝';
            if (subjectLower.includes('geography')) return '🌍';
            if (subjectLower.includes('computer')) return '💻';
            return '📚';
          };

          return (
            <div
              key={subject}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200"
            >
              <div className="text-center">
                <div className="text-5xl mb-4">{getSubjectIcon(subject)}</div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">{subject}</h3>
                <p className="text-gray-500 mb-2">{subcategoryCount} Bölmə{subcategoryCount !== 1 ? 'lər' : ''}</p>
                <p className="text-gray-500 mb-4">{totalQuizCount} Sınaq{totalQuizCount !== 1 ? 'lar' : ''}</p>
                <CategoryButton 
                  onClick={() => setSelectedSubject(subject)}
                  icon="🗂️"
                >
                  Araşdır {subject}
                </CategoryButton>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// User Personal Subjects Management Component
function UserMySubjects() {
  const [personalSubjects, setPersonalSubjects] = useState([]);
  const [availableSubjects, setAvailableSubjects] = useState({ global_subjects: [], personal_subjects: [], combined: [] });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newSubject, setNewSubject] = useState({
    name: '',
    description: '',
    subfolders: ['General']
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAvailableSubjects();
  }, []);

  const fetchAvailableSubjects = async () => {
    try {
      const response = await apiCall('/user/available-subjects');
      setAvailableSubjects(response.data);
      setPersonalSubjects(response.data.personal_subjects || []);
    } catch (error) {
      console.error('Error fetching available subjects:', error);
    }
  };

  const createPersonalSubject = async () => {
    if (!newSubject.name.trim()) {
      alert('Subject name is required');
      return;
    }

    setLoading(true);
    try {
      await apiCall('/user/personal-subject', {
        method: 'POST',
        data: {
          name: newSubject.name,
          description: newSubject.description,
          subfolders: newSubject.subfolders
        }
      });

      alert('Personal subject created successfully!');
      setShowCreateModal(false);
      setNewSubject({ name: '', description: '', subfolders: ['General'] });
      fetchAvailableSubjects();
    } catch (error) {
      alert('Error creating personal subject: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const addSubfolder = () => {
    setNewSubject({
      ...newSubject,
      subfolders: [...newSubject.subfolders, '']
    });
  };

  const updateSubfolder = (index, value) => {
    const updatedSubfolders = [...newSubject.subfolders];
    updatedSubfolders[index] = value;
    setNewSubject({ ...newSubject, subfolders: updatedSubfolders });
  };

  const removeSubfolder = (index) => {
    if (newSubject.subfolders.length > 1) {
      const updatedSubfolders = newSubject.subfolders.filter((_, i) => i !== index);
      setNewSubject({ ...newSubject, subfolders: updatedSubfolders });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">👤 My Personal Subjects</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition duration-200"
        >
          ➕ Create Personal Subject
        </button>
      </div>

      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">📚 Available Subjects Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-blue-700 font-medium">🌐 Global Subjects (Available to All):</p>
            <p className="text-blue-600">{availableSubjects.global_subjects.length} subjects</p>
            {availableSubjects.global_subjects.map(subject => (
              <div key={subject.id} className="ml-4 text-blue-600">
                • {subject.name} ({subject.subfolders.length} subfolders)
              </div>
            ))}
          </div>
          <div>
            <p className="text-blue-700 font-medium">👤 Your Personal Subjects:</p>
            <p className="text-blue-600">{availableSubjects.personal_subjects.length} subjects</p>
            {availableSubjects.personal_subjects.map(subject => (
              <div key={subject.id} className="ml-4 text-blue-600">
                • {subject.name} ({subject.subfolders.length} subfolders)
              </div>
            ))}
          </div>
        </div>
      </div>

      {personalSubjects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">You haven't created any personal subjects yet.</p>
          <p className="text-gray-400 text-sm mb-6">
            Personal subjects allow you to organize your quizzes with custom categories that are only visible to you.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition duration-200"
          >
            Create Your First Personal Subject
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {personalSubjects.map((subject) => (
            <div key={subject.id} className="border rounded-lg p-4">
              <div className="mb-2">
                <span className="inline-block px-2 py-1 rounded text-xs bg-purple-100 text-purple-800">
                  👤 Personal
                </span>
              </div>
              <h3 className="font-semibold text-gray-800 mb-2">{subject.name}</h3>
              {subject.description && (
                <p className="text-gray-600 text-sm mb-3">{subject.description}</p>
              )}
              
              <div className="mb-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Subfolders:</p>
                <div className="flex flex-wrap gap-1">
                  {subject.subfolders.map((subfolder, index) => (
                    <span key={index} className="inline-block px-2 py-1 rounded text-xs bg-gray-100 text-gray-700">
                      📁 {subfolder}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="text-xs text-gray-400 mb-3">
                Created: {new Date(subject.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Personal Subject Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">Create Personal Subject</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 font-semibold mb-2">Subject Name *</label>
                <input
                  type="text"
                  value={newSubject.name}
                  onChange={(e) => setNewSubject({ ...newSubject, name: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., My Programming Studies"
                  required
                />
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Description (Optional)</label>
                <textarea
                  value={newSubject.description}
                  onChange={(e) => setNewSubject({ ...newSubject, description: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Describe what this subject covers..."
                />
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Subfolders</label>
                {newSubject.subfolders.map((subfolder, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={subfolder}
                      onChange={(e) => updateSubfolder(index, e.target.value)}
                      className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                      placeholder="Subfolder name"
                    />
                    {newSubject.subfolders.length > 1 && (
                      <button
                        onClick={() => removeSubfolder(index)}
                        className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={addSubfolder}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  + Add Subfolder
                </button>
              </div>
            </div>

            <div className="flex gap-4 pt-6">
              <button
                onClick={createPersonalSubject}
                disabled={loading}
                className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold disabled:opacity-50"
              >
                {loading ? '⏳ Creating...' : '👤 Create Personal Subject'}
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                disabled={loading}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// User My Quizzes Management Component
function UserMyQuizzes({ setCurrentView }) {
  const [myQuizzes, setMyQuizzes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    fetchMyQuizzes();
  }, []);

  const fetchMyQuizzes = async () => {
    setLoading(true);
    try {
      const response = await apiCall('/user/my-quizzes');
      setMyQuizzes(response.data);
    } catch (error) {
      console.error('Error fetching my quizzes:', error);
    } finally {
      setLoading(false);
    }
  };

  const publishQuiz = async (quizId) => {
    try {
      await apiCall(`/user/quiz/${quizId}/publish`, {
        method: 'POST'
      });
      alert('Quiz published successfully! It is now visible to other users.');
      fetchMyQuizzes();
    } catch (error) {
      alert('Error publishing quiz: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteQuiz = async () => {
    if (!selectedQuiz) return;

    try {
      await apiCall(`/user/quiz/${selectedQuiz.id}`, {
        method: 'DELETE'
      });
      alert('Quiz deleted successfully!');
      setShowDeleteModal(false);
      setSelectedQuiz(null);
      fetchMyQuizzes();
    } catch (error) {
      alert('Error deleting quiz: ' + (error.response?.data?.detail || error.message));
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getOwnershipBadge = (quiz) => {
    return quiz.quiz_owner_type === 'user' 
      ? { color: 'bg-purple-100 text-purple-800', text: '👤 Your Quiz' }
      : { color: 'bg-blue-100 text-blue-800', text: '👑 Admin Quiz' };
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your quizzes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">📝 My Created Quizzes</h2>
        <button
          onClick={() => setCurrentView('create-quiz')}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition duration-200"
        >
          ➕ Create New Quiz
        </button>
      </div>

      <div className="mb-6 p-4 bg-green-50 rounded-lg">
        <h3 className="font-semibold text-green-800 mb-2">📊 Quiz Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-green-700 font-medium">Total Quizzes:</p>
            <p className="text-green-800 text-lg font-bold">{myQuizzes.length}</p>
          </div>
          <div>
            <p className="text-green-700 font-medium">Published:</p>
            <p className="text-green-800 text-lg font-bold">
              {myQuizzes.filter(q => !q.is_draft).length}
            </p>
          </div>
          <div>
            <p className="text-green-700 font-medium">Drafts:</p>
            <p className="text-green-800 text-lg font-bold">
              {myQuizzes.filter(q => q.is_draft).length}
            </p>
          </div>
          <div>
            <p className="text-green-700 font-medium">Total Attempts:</p>
            <p className="text-green-800 text-lg font-bold">
              {myQuizzes.reduce((sum, q) => sum + (q.total_attempts || 0), 0)}
            </p>
          </div>
        </div>
      </div>

      {myQuizzes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">You haven't created any quizzes yet.</p>
          <p className="text-gray-400 text-sm mb-6">
            Create your first quiz to share knowledge and test others!
          </p>
          <button
            onClick={() => setCurrentView('create-quiz')}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition duration-200"
          >
            Create Your First Quiz
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {myQuizzes.map((quiz) => {
            const ownershipBadge = getOwnershipBadge(quiz);
            return (
              <div key={quiz.id} className="border rounded-lg p-4">
                <div className="mb-2 flex flex-wrap gap-1">
                  <span className={`inline-block px-2 py-1 rounded text-xs ${ownershipBadge.color}`}>
                    {ownershipBadge.text}
                  </span>
                  <span className={`inline-block px-2 py-1 rounded text-xs ${
                    quiz.is_draft ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {quiz.is_draft ? '📝 Draft' : '✅ Published'}
                  </span>
                  <span className="inline-block px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                    {quiz.subject || 'General'}
                  </span>
                </div>

                {quiz.is_draft && (
                  <div className="mb-3 p-2 bg-orange-50 border-l-4 border-orange-400 rounded">
                    <p className="text-xs text-orange-700">
                      ⚠️ This quiz is in draft mode. Publish it to make it available to other users.
                    </p>
                  </div>
                )}

                <h3 className="font-semibold text-gray-800 mb-2">{quiz.title}</h3>
                <p className="text-gray-600 text-sm mb-2 line-clamp-2">{quiz.description}</p>
                
                <div className="flex justify-between items-center text-sm text-gray-500 mb-3">
                  <span>{quiz.category}</span>
                  <span>{quiz.total_questions} questions</span>
                </div>

                <div className="flex justify-between items-center text-sm text-gray-500 mb-3">
                  <span>{quiz.total_attempts || 0} attempts</span>
                  <span className="font-medium">Avg: {quiz.average_score || 0}%</span>
                </div>
                
                <div className="text-xs text-gray-400 mb-3">
                  Created: {formatDate(quiz.created_at)}
                  {quiz.updated_at !== quiz.created_at && (
                    <div>Updated: {formatDate(quiz.updated_at)}</div>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-1 text-xs">
                  {quiz.is_draft && (
                    <button
                      onClick={() => publishQuiz(quiz.id)}
                      className="bg-green-600 text-white py-2 rounded hover:bg-green-700 transition duration-200"
                    >
                      🚀 Publish
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setSelectedQuiz(quiz);
                      setShowDeleteModal(true);
                    }}
                    className="bg-red-600 text-white py-2 rounded hover:bg-red-700 transition duration-200"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Delete Quiz Confirmation Modal */}
      {showDeleteModal && selectedQuiz && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">🗑️</div>
              <h3 className="text-lg font-semibold mb-2">Delete Quiz?</h3>
              <p className="text-gray-600 text-sm">
                Are you sure you want to delete "{selectedQuiz.title}"?
              </p>
              <p className="text-red-600 text-sm mt-2">
                ⚠️ This action cannot be undone.
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={deleteQuiz}
                className="flex-1 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition duration-200 font-semibold"
              >
                Yes, Delete
              </button>
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setSelectedQuiz(null);
                }}
                className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// User Create Quiz Component with Combined Global/Personal Subjects
function UserCreateQuiz({ setCurrentView }) {
  const [availableSubjects, setAvailableSubjects] = useState({ global_subjects: [], personal_subjects: [], combined: [] });
  const [quizData, setQuizData] = useState({
    title: '',
    description: '',
    category: '',
    subject: '',
    subcategory: 'General',
    questions: []
  });
  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: '',
    question_type: 'multiple_choice',
    options: [
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ],
    multiple_correct: false,
    open_ended_answer: {
      expected_answers: [''],
      keywords: [],
      case_sensitive: false,
      partial_credit: true
    },
    points: 1,
    difficulty: 'medium',
    explanation: ''
  });
  const [showPreview, setShowPreview] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showPublishModal, setShowPublishModal] = useState(false);

  useEffect(() => {
    fetchAvailableSubjects();
  }, []);

  const fetchAvailableSubjects = async () => {
    try {
      const response = await apiCall('/user/available-subjects');
      setAvailableSubjects(response.data);
      
      // Set default subject if available
      if (response.data.combined.length > 0) {
        const firstSubject = response.data.combined[0];
        setQuizData(prev => ({
          ...prev,
          subject: firstSubject.name,
          subcategory: firstSubject.subfolders[0] || 'General'
        }));
      }
    } catch (error) {
      console.error('Error fetching available subjects:', error);
    }
  };

  const getCurrentSubjectData = () => {
    return availableSubjects.combined.find(s => s.name === quizData.subject);
  };

  const getAvailableSubfolders = () => {
    const currentSubject = getCurrentSubjectData();
    return currentSubject ? currentSubject.subfolders : ['General'];
  };

  const getSubjectDisplayName = (subject) => {
    const isGlobal = availableSubjects.global_subjects.some(s => s.name === subject.name);
    const isPersonal = availableSubjects.personal_subjects.some(s => s.name === subject.name);
    
    if (isGlobal) return `🌐 ${subject.name} (Global)`;
    if (isPersonal) return `👤 ${subject.name} (Personal)`;
    return subject.name;
  };

  const addQuestion = () => {
    if (!currentQuestion.question_text.trim()) {
      alert('Please enter a question text');
      return;
    }

    if (currentQuestion.question_type === 'multiple_choice') {
      const validOptions = currentQuestion.options.filter(opt => opt.text.trim());
      if (validOptions.length < 2) {
        alert('Please provide at least 2 answer options');
        return;
      }
      if (!validOptions.some(opt => opt.is_correct)) {
        alert('Please mark at least one correct answer');
        return;
      }
    } else if (currentQuestion.question_type === 'open_ended') {
      if (!currentQuestion.open_ended_answer.expected_answers.some(ans => ans.trim())) {
        alert('Please provide at least one expected answer');
        return;
      }
    }

    const newQuestion = {
      ...currentQuestion,
      id: Date.now().toString(),
      options: currentQuestion.question_type === 'multiple_choice' 
        ? currentQuestion.options.filter(opt => opt.text.trim())
        : []
    };

    setQuizData(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion]
    }));

    // Reset current question
    setCurrentQuestion({
      question_text: '',
      question_type: 'multiple_choice',
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ],
      multiple_correct: false,
      open_ended_answer: {
        expected_answers: [''],
        keywords: [],
        case_sensitive: false,
        partial_credit: true
      },
      points: 1,
      difficulty: 'medium',
      explanation: ''
    });
  };

  const removeQuestion = (index) => {
    setQuizData(prev => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== index)
    }));
  };

  const updateOption = (index, field, value) => {
    const updatedOptions = [...currentQuestion.options];
    if (field === 'is_correct' && !currentQuestion.multiple_correct) {
      // Single correct answer - uncheck others
      updatedOptions.forEach(opt => opt.is_correct = false);
    }
    updatedOptions[index][field] = value;
    setCurrentQuestion(prev => ({ ...prev, options: updatedOptions }));
  };

  const addOption = () => {
    if (currentQuestion.options.length < 6) {
      setCurrentQuestion(prev => ({
        ...prev,
        options: [...prev.options, { text: '', is_correct: false }]
      }));
    }
  };

  const removeOption = (index) => {
    if (currentQuestion.options.length > 2) {
      const updatedOptions = currentQuestion.options.filter((_, i) => i !== index);
      setCurrentQuestion(prev => ({ ...prev, options: updatedOptions }));
    }
  };

  const updateExpectedAnswer = (index, value) => {
    const updatedAnswers = [...currentQuestion.open_ended_answer.expected_answers];
    updatedAnswers[index] = value;
    setCurrentQuestion(prev => ({
      ...prev,
      open_ended_answer: { ...prev.open_ended_answer, expected_answers: updatedAnswers }
    }));
  };

  const addExpectedAnswer = () => {
    setCurrentQuestion(prev => ({
      ...prev,
      open_ended_answer: {
        ...prev.open_ended_answer,
        expected_answers: [...prev.open_ended_answer.expected_answers, '']
      }
    }));
  };

  const removeExpectedAnswer = (index) => {
    if (currentQuestion.open_ended_answer.expected_answers.length > 1) {
      const updatedAnswers = currentQuestion.open_ended_answer.expected_answers.filter((_, i) => i !== index);
      setCurrentQuestion(prev => ({
        ...prev,
        open_ended_answer: { ...prev.open_ended_answer, expected_answers: updatedAnswers }
      }));
    }
  };

  const createQuiz = async (shouldPublish = false) => {
    if (!quizData.title.trim() || !quizData.description.trim() || !quizData.category.trim()) {
      alert('Please fill in all required fields (title, description, category)');
      return;
    }

    if (quizData.questions.length === 0) {
      alert('Please add at least one question');
      return;
    }

    setLoading(true);
    try {
      const response = await apiCall('/user/quiz', {
        method: 'POST',
        data: {
          ...quizData,
          is_draft: !shouldPublish
        }
      });

      if (shouldPublish) {
        await apiCall(`/user/quiz/${response.data.id}/publish`, {
          method: 'POST'
        });
        alert('Quiz created and published successfully! It is now available to other users.');
      } else {
        alert('Quiz created as draft successfully! You can publish it later from "My Quizzes".');
      }

      setCurrentView('my-quizzes');
    } catch (error) {
      alert('Error creating quiz: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
      setShowPublishModal(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowPublishModal(true);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">➕ Create New Quiz</h2>
        <button
          onClick={() => setCurrentView('my-quizzes')}
          className="text-gray-600 hover:text-gray-800 transition duration-200"
        >
          ← Back to My Quizzes
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Quiz Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Quiz Title *</label>
            <input
              type="text"
              value={quizData.title}
              onChange={(e) => setQuizData(prev => ({ ...prev, title: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter quiz title"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Category *</label>
            <input
              type="text"
              value={quizData.category}
              onChange={(e) => setQuizData(prev => ({ ...prev, category: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Education, Technology, Science"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-gray-700 font-semibold mb-2">Description *</label>
          <textarea
            value={quizData.description}
            onChange={(e) => setQuizData(prev => ({ ...prev, description: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            rows="3"
            placeholder="Describe what this quiz covers"
            required
          />
        </div>

        {/* Combined Subject Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Subject *</label>
            <select
              value={quizData.subject}
              onChange={(e) => setQuizData(prev => ({ 
                ...prev, 
                subject: e.target.value,
                subcategory: 'General'
              }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select a subject</option>
              {availableSubjects.combined.map(subject => (
                <option key={subject.id} value={subject.name}>
                  {getSubjectDisplayName(subject)}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              🌐 Global subjects are available to all users, 👤 Personal subjects are yours only
            </p>
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Subcategory *</label>
            <select
              value={quizData.subcategory}
              onChange={(e) => setQuizData(prev => ({ ...prev, subcategory: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            >
              {getAvailableSubfolders().map(subfolder => (
                <option key={subfolder} value={subfolder}>{subfolder}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Subject Info Display */}
        {quizData.subject && (
          <div className="p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Selected:</strong> {getSubjectDisplayName(getCurrentSubjectData())} → {quizData.subcategory}
            </p>
          </div>
        )}

        {/* Question Builder */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Add Questions</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Question Text *</label>
              <textarea
                value={currentQuestion.question_text}
                onChange={(e) => setCurrentQuestion(prev => ({ ...prev, question_text: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                rows="2"
                placeholder="Enter your question here"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-gray-700 font-semibold mb-2">Question Type</label>
                <select
                  value={currentQuestion.question_type}
                  onChange={(e) => setCurrentQuestion(prev => ({ ...prev, question_type: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="multiple_choice">Multiple Choice</option>
                  <option value="open_ended">Open Ended</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Points</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={currentQuestion.points}
                  onChange={(e) => setCurrentQuestion(prev => ({ ...prev, points: parseInt(e.target.value) }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Difficulty</label>
                <select
                  value={currentQuestion.difficulty}
                  onChange={(e) => setCurrentQuestion(prev => ({ ...prev, difficulty: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            {/* Multiple Choice Options */}
            {currentQuestion.question_type === 'multiple_choice' && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-gray-700 font-semibold">Answer Options</label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={currentQuestion.multiple_correct}
                      onChange={(e) => setCurrentQuestion(prev => ({ ...prev, multiple_correct: e.target.checked }))}
                      className="mr-2"
                    />
                    Allow multiple correct answers
                  </label>
                </div>
                
                {currentQuestion.options.map((option, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type={currentQuestion.multiple_correct ? 'checkbox' : 'radio'}
                      name="correct_answer"
                      checked={option.is_correct}
                      onChange={(e) => updateOption(index, 'is_correct', e.target.checked)}
                      className="mt-3"
                    />
                    <input
                      type="text"
                      value={option.text}
                      onChange={(e) => updateOption(index, 'text', e.target.value)}
                      className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                      placeholder={`Option ${index + 1}`}
                    />
                    {currentQuestion.options.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeOption(index)}
                        className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
                
                {currentQuestion.options.length < 6 && (
                  <button
                    type="button"
                    onClick={addOption}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    + Add Option
                  </button>
                )}
              </div>
            )}

            {/* Open Ended Answers */}
            {currentQuestion.question_type === 'open_ended' && (
              <div>
                <label className="block text-gray-700 font-semibold mb-2">Expected Answers</label>
                {currentQuestion.open_ended_answer.expected_answers.map((answer, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={answer}
                      onChange={(e) => updateExpectedAnswer(index, e.target.value)}
                      className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                      placeholder={`Expected answer ${index + 1}`}
                    />
                    {currentQuestion.open_ended_answer.expected_answers.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeExpectedAnswer(index)}
                        className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
                
                <button
                  type="button"
                  onClick={addExpectedAnswer}
                  className="text-blue-600 hover:text-blue-800 text-sm mb-3"
                >
                  + Add Expected Answer
                </button>

                <div className="flex items-center gap-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={currentQuestion.open_ended_answer.case_sensitive}
                      onChange={(e) => setCurrentQuestion(prev => ({
                        ...prev,
                        open_ended_answer: { ...prev.open_ended_answer, case_sensitive: e.target.checked }
                      }))}
                      className="mr-2"
                    />
                    Case sensitive
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={currentQuestion.open_ended_answer.partial_credit}
                      onChange={(e) => setCurrentQuestion(prev => ({
                        ...prev,
                        open_ended_answer: { ...prev.open_ended_answer, partial_credit: e.target.checked }
                      }))}
                      className="mr-2"
                    />
                    Partial credit
                  </label>
                </div>
              </div>
            )}

            <div>
              <label className="block text-gray-700 font-semibold mb-2">Explanation (Optional)</label>
              <textarea
                value={currentQuestion.explanation}
                onChange={(e) => setCurrentQuestion(prev => ({ ...prev, explanation: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                rows="2"
                placeholder="Explain the correct answer (shown to users after answering)"
              />
            </div>

            <button
              type="button"
              onClick={addQuestion}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
            >
              ➕ Add Question
            </button>
          </div>
        </div>

        {/* Questions Preview */}
        {quizData.questions.length > 0 && (
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Questions Added ({quizData.questions.length})
            </h3>
            
            <div className="space-y-3">
              {quizData.questions.map((question, index) => (
                <div key={question.id} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="font-medium text-gray-800">
                        {index + 1}. {question.question_text}
                      </p>
                      <div className="flex gap-2 mt-1">
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                          {question.question_type === 'multiple_choice' ? 'Multiple Choice' : 'Open Ended'}
                        </span>
                        <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                          {question.points} {question.points === 1 ? 'point' : 'points'}
                        </span>
                        <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded">
                          {question.difficulty}
                        </span>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeQuestion(index)}
                      className="ml-4 px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Submit Buttons */}
        <div className="flex gap-4 pt-6 border-t">
          <button
            type="submit"
            disabled={loading || quizData.questions.length === 0}
            className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold disabled:opacity-50"
          >
            {loading ? '⏳ Creating...' : '🚀 Create Quiz'}
          </button>
          <button
            type="button"
            onClick={() => setCurrentView('my-quizzes')}
            className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
          >
            Cancel
          </button>
        </div>
      </form>

      {/* Publish Modal */}
      {showPublishModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center mb-6">
              <div className="text-4xl mb-4">🚀</div>
              <h3 className="text-lg font-semibold mb-2">Publish Quiz?</h3>
              <p className="text-gray-600 text-sm">
                Would you like to publish this quiz immediately or save it as a draft?
              </p>
            </div>

            <div className="space-y-3 mb-6">
              <div className="p-3 bg-green-50 border border-green-200 rounded">
                <p className="text-sm text-green-800">
                  <strong>✅ Publish Now:</strong> Quiz will be immediately available to other users
                </p>
              </div>
              <div className="p-3 bg-orange-50 border border-orange-200 rounded">
                <p className="text-sm text-orange-800">
                  <strong>📝 Save as Draft:</strong> You can publish it later from "My Quizzes"
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => createQuiz(true)}
                disabled={loading}
                className="bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold disabled:opacity-50"
              >
                {loading ? '⏳ Publishing...' : '✅ Publish Now'}
              </button>
              <button
                onClick={() => createQuiz(false)}
                disabled={loading}
                className="bg-orange-600 text-white py-3 rounded-lg hover:bg-orange-700 transition duration-200 font-semibold disabled:opacity-50"
              >
                {loading ? '⏳ Saving...' : '📝 Save as Draft'}
              </button>
            </div>
            
            <button
              onClick={() => setShowPublishModal(false)}
              disabled={loading}
              className="w-full mt-3 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition duration-200"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Admin Q&A Management Component
function AdminQAManagement() {
  const [qaStats, setQAStats] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState('stats');

  useEffect(() => {
    fetchQAStats();
    if (currentTab === 'questions') {
      fetchAllQuestions();
    }
  }, [currentTab]);

  const fetchQAStats = async () => {
    try {
      const response = await apiCall('/admin/qa-stats');
      setQAStats(response.data);
    } catch (error) {
      console.error('Error fetching Q&A stats:', error);
    }
  };

  const fetchAllQuestions = async () => {
    setLoading(true);
    try {
      const response = await apiCall('/questions?limit=50&sort_by=created_at&sort_order=desc');
      setQuestions(response.data.questions || []);
    } catch (error) {
      console.error('Error fetching questions:', error);
      setQuestions([]);
    }
    setLoading(false);
  };

  const togglePinQuestion = async (questionId, currentPinStatus) => {
    try {
      await apiCall(`/admin/questions/${questionId}/pin`, {
        method: 'PUT'
      });
      // Refresh the questions list
      fetchAllQuestions();
    } catch (error) {
      console.error('Error toggling pin:', error);
      alert('Failed to toggle pin status');
    }
  };

  const deleteQuestion = async (questionId) => {
    if (!window.confirm('Are you sure you want to delete this question? This action cannot be undone.')) {
      return;
    }

    try {
      await apiCall(`/questions/${questionId}`, {
        method: 'DELETE'
      });
      // Refresh the questions list
      fetchAllQuestions();
      fetchQAStats(); // Update stats
    } catch (error) {
      console.error('Error deleting question:', error);
      alert('Failed to delete question');
    }
  };

  if (!qaStats && currentTab === 'stats') {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading Q&A statistics...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">💬 Q&A Forum Management</h2>

      {/* Tabs */}
      <div className="flex flex-wrap border-b mb-6">
        <button
          onClick={() => setCurrentTab('stats')}
          className={`px-4 py-2 font-medium transition duration-200 ${
            currentTab === 'stats'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📊 Statistics
        </button>
        <button
          onClick={() => setCurrentTab('questions')}
          className={`px-4 py-2 font-medium transition duration-200 ${
            currentTab === 'questions'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          ❓ Manage Questions
        </button>
      </div>

      {/* Statistics Tab */}
      {currentTab === 'stats' && qaStats && (
        <div className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-600 text-sm font-medium">Total Questions</p>
                  <p className="text-2xl font-bold text-blue-800">{qaStats.total_questions}</p>
                </div>
                <div className="text-3xl">❓</div>
              </div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-600 text-sm font-medium">Total Answers</p>
                  <p className="text-2xl font-bold text-green-800">{qaStats.total_answers}</p>
                </div>
                <div className="text-3xl">💬</div>
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-600 text-sm font-medium">Discussions</p>
                  <p className="text-2xl font-bold text-purple-800">{qaStats.total_discussions}</p>
                </div>
                <div className="text-3xl">💭</div>
              </div>
            </div>
          </div>

          {/* Questions by Status */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-3">Questions by Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {qaStats.questions_by_status.open}
                </div>
                <div className="text-sm text-gray-600">Open Questions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {qaStats.questions_by_status.answered}
                </div>
                <div className="text-sm text-gray-600">Answered Questions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">
                  {qaStats.questions_by_status.closed}
                </div>
                <div className="text-sm text-gray-600">Closed Questions</div>
              </div>
            </div>
          </div>

          {/* Questions by Subject */}
          {qaStats.questions_by_subject.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3">Questions by Subject</h3>
              <div className="space-y-2">
                {qaStats.questions_by_subject.map((subject, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-700">
                      📖 {subject._id || 'No Subject'}
                    </span>
                    <span className="font-semibold text-blue-600">
                      {subject.count} questions
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Questions Management Tab */}
      {currentTab === 'questions' && (
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading questions...</p>
            </div>
          ) : questions.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🤔</div>
              <p className="text-gray-600">No questions found</p>
            </div>
          ) : (
            questions.map((question) => (
              <AdminPostContainer
                key={question.id}
                isAdmin={question.user && question.user.role === 'admin'}
                className="border rounded-lg p-4 mb-4"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      {question.is_pinned && (
                        <span className="px-2 py-1 rounded text-xs bg-yellow-100 text-yellow-800 font-medium">
                          📌 Pinned
                        </span>
                      )}
                      {question.has_accepted_answer && (
                        <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-800 font-medium">
                          ✅ Answered
                        </span>
                      )}
                      {question.subject && (
                        <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                          📖 {question.subject}
                        </span>
                      )}
                    </div>
                    
                    <h3 className={`font-semibold mb-2 ${
                      question.user && question.user.role === 'admin'
                        ? 'text-purple-800 dark:text-purple-300 font-bold'
                        : 'text-gray-800 dark:text-gray-200'
                    }`}>{question.title}</h3>
                    
                    <p className={`text-sm mb-2 line-clamp-2 ${
                      question.user && question.user.role === 'admin'
                        ? 'text-purple-700 dark:text-purple-400 font-medium'
                        : 'text-gray-600 dark:text-gray-400'
                    }`}>{question.content}</p>
                    
                    <div className="flex items-center text-sm space-x-4">
                      <div className="flex items-center space-x-2">
                        <span>👤</span>
                        <AdminName 
                          name={question.user ? question.user.name : 'Unknown User'}
                          role={question.user?.role}
                        />
                        {question.user && question.user.role === 'admin' && (
                          <AdminBadge size="default" />
                        )}
                      </div>
                      <span className="text-gray-500">💬 {question.answer_count || 0} answers</span>
                      <span className="text-gray-500">👍 {(question.upvotes || 0) - (question.downvotes || 0)} votes</span>
                      <span className="text-gray-500">{new Date(question.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => togglePinQuestion(question.id, question.is_pinned)}
                      className={`px-3 py-1 rounded text-xs transition duration-200 ${
                        question.is_pinned
                          ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {question.is_pinned ? '📌 Unpin' : '📌 Pin'}
                    </button>
                    <button
                      onClick={() => deleteQuestion(question.id)}
                      className="px-3 py-1 rounded text-xs bg-red-100 text-red-800 hover:bg-red-200 transition duration-200"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              </AdminPostContainer>
            ))
          )}
        </div>
      )}
    </div>
  );
}

// ====================================================================
// Q&A DISCUSSION SYSTEM COMPONENTS
// ====================================================================

// Q&A Forum Main Component
function QAForum({ user }) {
  const [currentTab, setCurrentTab] = useState('all-questions');
  const [questions, setQuestions] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAskQuestion, setShowAskQuestion] = useState(false);

  useEffect(() => {
    if (currentTab === 'all-questions') {
      fetchQuestions();
    } else if (currentTab === 'by-subject') {
      fetchAvailableSubjects();
    }
  }, [currentTab]);

  const fetchQuestions = async (subject = '', subcategory = '') => {
    setLoading(true);
    try {
      let url = '/questions?limit=20&sort_by=created_at&sort_order=desc';
      if (subject) url += `&subject=${encodeURIComponent(subject)}`;
      if (subcategory) url += `&subcategory=${encodeURIComponent(subcategory)}`;
      
      const response = await apiCall(url);
      setQuestions(response.data.questions || []);
    } catch (error) {
      console.error('Error fetching questions:', error);
      setQuestions([]);
    }
    setLoading(false);
  };

  const fetchAvailableSubjects = async () => {
    try {
      const response = await apiCall('/subjects-available');
      setAvailableSubjects(response.data.subjects || []);
    } catch (error) {
      console.error('Error fetching subjects:', error);
      setAvailableSubjects([]);
    }
  };

  const handleSubjectSelect = (subject) => {
    setSelectedSubject(subject);
    fetchQuestions(subject);
  };

  if (selectedQuestion) {
    return (
      <QuestionDetail 
        question={selectedQuestion}
        user={user}
        onBack={() => setSelectedQuestion(null)}
        onQuestionUpdate={(updatedQuestion) => {
          setQuestions(questions.map(q => q.id === updatedQuestion.id ? updatedQuestion : q));
          setSelectedQuestion(updatedQuestion);
        }}
      />
    );
  }

  if (showAskQuestion) {
    return (
      <AskQuestionForm
        user={user}
        availableSubjects={availableSubjects}
        onCancel={() => setShowAskQuestion(false)}
        onQuestionCreated={(newQuestion) => {
          setQuestions([newQuestion, ...questions]);
          setShowAskQuestion(false);
        }}
      />
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-2">💬 Q&A Forum</h1>
            <p className="text-gray-600">Ask questions, share knowledge, and learn together</p>
          </div>
          <button
            onClick={() => setShowAskQuestion(true)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
          >
            ➕ Ask Question
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm mb-6">
        <div className="flex flex-wrap border-b">
          <button
            onClick={() => setCurrentTab('all-questions')}
            className={`px-4 sm:px-6 py-3 font-medium transition duration-200 ${
              currentTab === 'all-questions'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            🌐 All Questions
          </button>
          <button
            onClick={() => setCurrentTab('by-subject')}
            className={`px-4 sm:px-6 py-3 font-medium transition duration-200 ${
              currentTab === 'by-subject'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            📚 By Subject
          </button>
        </div>

        {/* Subject Filter for By Subject Tab */}
        {currentTab === 'by-subject' && (
          <div className="p-4 border-b bg-gray-50">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => {
                  setSelectedSubject('');
                  fetchQuestions();
                }}
                className={`px-3 py-2 rounded-lg text-sm transition duration-200 ${
                  selectedSubject === ''
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 border hover:bg-gray-50'
                }`}
              >
                All Subjects
              </button>
              {availableSubjects.map((subject) => (
                <button
                  key={subject}
                  onClick={() => handleSubjectSelect(subject)}
                  className={`px-3 py-2 rounded-lg text-sm transition duration-200 ${
                    selectedSubject === subject
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 border hover:bg-gray-50'
                  }`}
                >
                  📖 {subject}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Questions List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading questions...</p>
          </div>
        ) : questions.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">🤔</div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No questions yet</h3>
            <p className="text-gray-600 mb-6">
              {selectedSubject 
                ? `No questions found for ${selectedSubject}. Be the first to ask!`
                : 'Be the first to ask a question in the forum!'
              }
            </p>
            <button
              onClick={() => setShowAskQuestion(true)}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition duration-200"
            >
              Ask First Question
            </button>
          </div>
        ) : (
          questions.map((question) => (
            <QuestionCard
              key={question.id}
              question={question}
              onClick={() => setSelectedQuestion(question)}
              currentUser={user}
            />
          ))
        )}
      </div>
    </div>
  );
}

// Question Card Component
function QuestionCard({ question, onClick, currentUser }) {
  const [voting, setVoting] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [bookmarking, setBookmarking] = useState(false);

  // Check bookmark status when component mounts
  useEffect(() => {
    if (currentUser) {
      checkBookmarkStatus();
    }
  }, [question.id, currentUser]);

  const checkBookmarkStatus = async () => {
    try {
      const response = await apiCall(`/bookmarks/check/${question.id}?item_type=question`);
      setIsBookmarked(response.data.is_bookmarked);
    } catch (error) {
      console.error('Error checking bookmark status:', error);
    }
  };

  const handleBookmark = async (e) => {
    e.stopPropagation(); // Prevent opening question detail
    if (bookmarking || !currentUser) return;
    
    setBookmarking(true);
    try {
      if (isBookmarked) {
        await apiCall(`/bookmarks/${question.id}?item_type=question`, { method: 'DELETE' });
        setIsBookmarked(false);
      } else {
        await apiCall('/bookmarks', {
          method: 'POST',
          data: { item_id: question.id, item_type: 'question' }
        });
        setIsBookmarked(true);
      }
    } catch (error) {
      console.error('Error toggling bookmark:', error);
      alert('Failed to bookmark: ' + (error.response?.data?.detail || 'Unknown error'));
    }
    setBookmarking(false);
  };

  const handleVote = async (voteType, e) => {
    e.stopPropagation(); // Prevent opening question detail
    if (voting) return;
    
    setVoting(true);
    try {
      await apiCall(`/questions/${question.id}/vote`, {
        method: 'POST',
        data: { vote_type: voteType }
      });
      // In a real app, you'd update the question data here
      // For now, we'll just refresh on next load
    } catch (error) {
      console.error('Error voting:', error);
      alert('Failed to vote: ' + (error.response?.data?.detail || 'Unknown error'));
    }
    setVoting(false);
  };

  const getTimeSince = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const isOwnQuestion = currentUser && question.user && question.user.id === currentUser.id;
  const hasUpvoted = currentUser && question.upvoted_by && question.upvoted_by.includes(currentUser.id);
  const hasDownvoted = currentUser && question.downvoted_by && question.downvoted_by.includes(currentUser.id);

  return (
    <AdminPostContainer
      isAdmin={question.user && question.user.role === 'admin'}
      className="bg-white rounded-lg shadow-sm border hover:shadow-md transition duration-200 cursor-pointer"
      onClick={onClick}
    >
      <div className="p-6">
        <div className="flex gap-4">
          {/* Voting Section */}
          <div className="flex flex-col items-center space-y-1 mr-4">
            <button
              onClick={(e) => handleVote(hasUpvoted ? 'remove' : 'upvote', e)}
              disabled={voting || isOwnQuestion}
              className={`p-2 rounded-full transition duration-200 ${
                hasUpvoted
                  ? 'text-green-600 bg-green-50'
                  : 'text-gray-400 hover:text-green-600 hover:bg-green-50'
              } ${(voting || isOwnQuestion) ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              ▲
            </button>
            <span className="text-sm font-semibold text-gray-700">
              {(question.upvotes || 0) - (question.downvotes || 0)}
            </span>
            <button
              onClick={(e) => handleVote(hasDownvoted ? 'remove' : 'downvote', e)}
              disabled={voting || isOwnQuestion}
              className={`p-2 rounded-full transition duration-200 ${
                hasDownvoted
                  ? 'text-red-600 bg-red-50'
                  : 'text-gray-400 hover:text-red-600 hover:bg-red-50'
              } ${(voting || isOwnQuestion) ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              ▼
            </button>
          </div>

          {/* Question Content */}
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              {question.is_pinned && (
                <span className="inline-block px-2 py-1 rounded text-xs bg-yellow-100 text-yellow-800 font-medium">
                  📌 Pinned
                </span>
              )}
              {question.has_accepted_answer && (
                <span className="inline-block px-2 py-1 rounded text-xs bg-green-100 text-green-800 font-medium">
                  ✅ Answered
                </span>
              )}
              {question.subject && (
                <span className="inline-block px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                  📖 {question.subject}
                </span>
              )}
              {question.subcategory && question.subcategory !== 'General' && (
                <span className="inline-block px-2 py-1 rounded text-xs bg-purple-100 text-purple-800">
                  📁 {question.subcategory}
                </span>
              )}
            </div>

            <h3 className={`text-lg font-semibold mb-2 line-clamp-2 ${
              question.user && question.user.role === 'admin'
                ? 'text-purple-800 dark:text-purple-300 font-bold'
                : 'text-gray-800 dark:text-gray-200'
            }`}>
              {question.title}
            </h3>
            
            <p className={`text-sm mb-4 line-clamp-2 ${
              question.user && question.user.role === 'admin'
                ? 'text-purple-700 dark:text-purple-400 font-medium'
                : 'text-gray-600 dark:text-gray-400'
            }`}>
              {question.content}
            </p>

            {question.image && (
              <div className="mb-4">
                <img
                  src={question.image}
                  alt="Question"
                  className="max-w-xs max-h-32 object-cover rounded-lg"
                />
              </div>
            )}

            <div className="flex flex-wrap items-center justify-between text-sm text-gray-500">
              <div className="flex items-center space-x-4">
                <span className="flex items-center space-x-1">
                  <span>💬</span>
                  <span>{question.answer_count || 0} answers</span>
                </span>
                <div className="flex items-center space-x-2">
                  <span className="flex items-center space-x-1">
                    <span>👤</span>
                    <AdminName 
                      name={question.user ? question.user.name : 'Unknown User'}
                      role={question.user?.role}
                    />
                  </span>
                  {question.user && question.user.role === 'admin' && (
                    <AdminBadge size="default" />
                  )}
                  {question.user && (
                    <FollowButton 
                      userId={question.user.id} 
                      className="text-xs px-2 py-1"
                    />
                  )}
                </div>
                {currentUser && (
                  <button
                    onClick={handleBookmark}
                    disabled={bookmarking}
                    className={`flex items-center space-x-1 px-2 py-1 rounded transition duration-200 ${
                      isBookmarked
                        ? 'text-blue-600 bg-blue-50 hover:bg-blue-100'
                        : 'text-gray-400 hover:text-blue-600 hover:bg-blue-50'
                    } ${bookmarking ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <span>{isBookmarked ? '🔖' : '📄'}</span>
                    <span className="text-xs">{isBookmarked ? 'Saved' : 'Save'}</span>
                  </button>
                )}
              </div>
              <span>{getTimeSince(question.created_at)}</span>
            </div>
          </div>
        </div>
      </div>
    </AdminPostContainer>
  );
}

// Ask Question Form Component
function AskQuestionForm({ user, availableSubjects, onCancel, onQuestionCreated }) {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    subject: '',
    subcategory: 'General',
    tags: [],
    image: null
  });
  const [loading, setLoading] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const fileInputRef = useRef(null);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('Image size must be less than 5MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setFormData({ ...formData, image: e.target.result });
    };
    reader.readAsDataURL(file);
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim()) && formData.tags.length < 5) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.content.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await apiCall('/questions', {
        method: 'POST',
        data: {
          title: formData.title.trim(),
          content: formData.content.trim(),
          subject: formData.subject || null,
          subcategory: formData.subcategory || 'General',
          tags: formData.tags,
          image: formData.image
        }
      });

      // Add user info to the response for immediate display
      const newQuestion = {
        ...response.data,
        user: { id: user.id, name: user.name, role: user.role }
      };

      onQuestionCreated(newQuestion);
    } catch (error) {
      console.error('Error creating question:', error);
      alert('Failed to create question: ' + (error.response?.data?.detail || 'Unknown error'));
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">❓ Ask a Question</h1>
          <button
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Question Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="What's your question? Be specific and clear..."
              required
              maxLength={200}
            />
            <p className="text-xs text-gray-500 mt-1">
              {formData.title.length}/200 characters
            </p>
          </div>

          {/* Content */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Question Details *
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({...formData, content: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows="6"
              placeholder="Provide more details about your question. Include any relevant context, what you've tried, and what specific help you need..."
              required
            />
          </div>

          {/* Subject and Subcategory */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Subject (Optional)
              </label>
              <select
                value={formData.subject}
                onChange={(e) => setFormData({...formData, subject: e.target.value, subcategory: 'General'})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a subject...</option>
                {availableSubjects.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Subcategory
              </label>
              <input
                type="text"
                value={formData.subcategory}
                onChange={(e) => setFormData({...formData, subcategory: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="General"
              />
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Tags (Optional)
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Add a tag and press Enter"
                maxLength={20}
              />
              <button
                type="button"
                onClick={addTag}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                >
                  #{tag}
                  <button
                    type="button"
                    onClick={() => removeTag(tag)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Image Upload */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Image (Optional)
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
              {formData.image ? (
                <div className="text-center">
                  <img
                    src={formData.image}
                    alt="Preview"
                    className="max-w-full max-h-48 mx-auto rounded-lg mb-4"
                  />
                  <button
                    type="button"
                    onClick={() => setFormData({...formData, image: null})}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove Image
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <div className="text-gray-400 mb-4">
                    <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition duration-200"
                  >
                    Choose Image
                  </button>
                  <p className="text-xs text-gray-500 mt-2">PNG, JPG up to 5MB</p>
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-4 pt-6">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold disabled:opacity-50"
            >
              {loading ? 'Posting...' : '✓ Post Question'}
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition duration-200"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Question Detail Component (placeholder for now)
function QuestionDetail({ question, user, onBack, onQuestionUpdate }) {
  const [answers, setAnswers] = useState([]);
  const [discussions, setDiscussions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAnswerForm, setShowAnswerForm] = useState(false);
  const [newAnswer, setNewAnswer] = useState({ content: '', image: null });
  const [newDiscussion, setNewDiscussion] = useState({ message: '', image: null });
  const [submittingAnswer, setSubmittingAnswer] = useState(false);
  const [submittingDiscussion, setSubmittingDiscussion] = useState(false);

  useEffect(() => {
    fetchQuestionDetail();
  }, [question.id]);

  const fetchQuestionDetail = async () => {
    setLoading(true);
    try {
      const response = await apiCall(`/questions/${question.id}`);
      setAnswers(response.data.answers || []);
      setDiscussions(response.data.discussions || []);
    } catch (error) {
      console.error('Error fetching question detail:', error);
    }
    setLoading(false);
  };

  const submitAnswer = async (e) => {
    e.preventDefault();
    if (!newAnswer.content.trim()) return;

    setSubmittingAnswer(true);
    try {
      const response = await apiCall(`/questions/${question.id}/answers`, {
        method: 'POST',
        data: newAnswer
      });
      
      const answerWithUser = {
        ...response.data,
        user: { id: user.id, name: user.name, role: user.role }
      };
      
      setAnswers([...answers, answerWithUser]);
      setNewAnswer({ content: '', image: null });
      setShowAnswerForm(false);
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer: ' + (error.response?.data?.detail || 'Unknown error'));
    }
    setSubmittingAnswer(false);
  };

  const submitDiscussion = async (e) => {
    e.preventDefault();
    if (!newDiscussion.message.trim()) return;

    setSubmittingDiscussion(true);
    try {
      const response = await apiCall(`/questions/${question.id}/discussions`, {
        method: 'POST',
        data: newDiscussion
      });
      
      const discussionWithUser = {
        ...response.data,
        user: { id: user.id, name: user.name, role: user.role }
      };
      
      setDiscussions([...discussions, discussionWithUser]);
      setNewDiscussion({ message: '', image: null });
    } catch (error) {
      console.error('Error submitting discussion:', error);
      alert('Failed to submit message: ' + (error.response?.data?.detail || 'Unknown error'));
    }
    setSubmittingDiscussion(false);
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading question...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="mb-4 flex items-center text-blue-600 hover:text-blue-800 transition duration-200"
      >
        ← Back to Questions
      </button>

      {/* Question Detail */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex gap-4">
          {/* Voting Section */}
          <div className="flex flex-col items-center space-y-2">
            <button className="p-2 rounded-full text-gray-400 hover:text-green-600 hover:bg-green-50">
              ▲
            </button>
            <span className="text-lg font-semibold text-gray-700">
              {(question.upvotes || 0) - (question.downvotes || 0)}
            </span>
            <button className="p-2 rounded-full text-gray-400 hover:text-red-600 hover:bg-red-50">
              ▼
            </button>
          </div>

          {/* Question Content */}
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-4">
              {question.is_pinned && (
                <span className="px-2 py-1 rounded text-xs bg-yellow-100 text-yellow-800 font-medium">
                  📌 Pinned
                </span>
              )}
              {question.has_accepted_answer && (
                <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-800 font-medium">
                  ✅ Answered
                </span>
              )}
              {question.subject && (
                <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                  📖 {question.subject}
                </span>
              )}
            </div>

            <h1 className="text-2xl font-bold text-gray-800 mb-4">{question.title}</h1>
            
            <div className="prose max-w-none mb-4">
              <div className="text-gray-700 whitespace-pre-wrap">{question.content}</div>
            </div>

            {question.image && (
              <div className="mb-4">
                <img
                  src={question.image}
                  alt="Question"
                  className="max-w-full max-h-96 rounded-lg shadow-sm"
                />
              </div>
            )}

            <div className="flex items-center text-sm text-gray-500 space-x-4">
              <div className="flex items-center space-x-2">
                <span className="flex items-center space-x-1">
                  <span>👤</span>
                  <AdminName 
                    name={question.user ? question.user.name : 'Unknown User'}
                    role={question.user?.role}
                  />
                </span>
                {question.user && question.user.role === 'admin' && (
                  <AdminBadge size="default" />
                )}
              </div>
              <span>Asked {new Date(question.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Answers Section */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">
            {answers.length} Answer{answers.length !== 1 ? 's' : ''}
          </h2>
          <button
            onClick={() => setShowAnswerForm(!showAnswerForm)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition duration-200"
          >
            {showAnswerForm ? 'Cancel' : 'Write Answer'}
          </button>
        </div>

        {/* Answer Form */}
        {showAnswerForm && (
          <form onSubmit={submitAnswer} className="mb-6 p-4 border rounded-lg bg-gray-50">
            <textarea
              value={newAnswer.content}
              onChange={(e) => setNewAnswer({...newAnswer, content: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-3"
              rows="4"
              placeholder="Write your answer..."
              required
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={submittingAnswer}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition duration-200 disabled:opacity-50"
              >
                {submittingAnswer ? 'Submitting...' : 'Submit Answer'}
              </button>
              <button
                type="button"
                onClick={() => setShowAnswerForm(false)}
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition duration-200"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {/* Answers List */}
        <div className="space-y-6">
          {answers.map((answer) => (
            <AdminPostContainer
              key={answer.id}
              isAdmin={answer.user && answer.user.role === 'admin'}
              className={`border-l-4 pl-6 ${
                answer.user && answer.user.role === 'admin' 
                  ? 'border-purple-400' 
                  : 'border-gray-200'
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-2">
                  <AdminName 
                    name={answer.user ? answer.user.name : 'Unknown User'}
                    role={answer.user?.role}
                    className="font-medium"
                  />
                  {answer.user && answer.user.role === 'admin' && (
                    <AdminBadge size="default" />
                  )}
                  <span className="text-sm text-gray-500">
                    {new Date(answer.created_at).toLocaleDateString()}
                  </span>
                  {answer.is_accepted && (
                    <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-800 font-medium">
                      ✅ Accepted
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">
                    {(answer.upvotes || 0) - (answer.downvotes || 0)} votes
                  </span>
                </div>
              </div>
              <div className={`whitespace-pre-wrap ${
                answer.user && answer.user.role === 'admin'
                  ? 'text-purple-800 dark:text-purple-300 font-medium'
                  : 'text-gray-700 dark:text-gray-300'
              }`}>{answer.content}</div>
              {answer.image && (
                <img
                  src={answer.image}
                  alt="Answer"
                  className="mt-3 max-w-md max-h-64 rounded-lg shadow-sm"
                />
              )}
              
              {/* Emoji Reactions */}
              <EmojiReactions answerId={answer.id} currentUser={user} />
            </AdminPostContainer>
          ))}
        </div>
      </div>

      {/* Discussion Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">
          Discussion ({discussions.length})
        </h2>

        {/* Discussion Form */}
        <form onSubmit={submitDiscussion} className="mb-6 p-4 border rounded-lg bg-gray-50">
          <textarea
            value={newDiscussion.message}
            onChange={(e) => setNewDiscussion({...newDiscussion, message: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-3"
            rows="3"
            placeholder="Join the discussion..."
            required
          />
          <button
            type="submit"
            disabled={submittingDiscussion}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200 disabled:opacity-50"
          >
            {submittingDiscussion ? 'Posting...' : 'Post Message'}
          </button>
        </form>

        {/* Discussion Messages */}
        <div className="space-y-4">
          {discussions.map((discussion) => (
            <div key={discussion.id} className="flex space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-semibold">
                    {discussion.user && discussion.user.name ? discussion.user.name.charAt(0).toUpperCase() : 'U'}
                  </span>
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-medium text-gray-800">{discussion.user ? discussion.user.name : 'Unknown User'}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(discussion.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="text-gray-700 text-sm whitespace-pre-wrap">{discussion.message}</div>
                {discussion.image && (
                  <img
                    src={discussion.image}
                    alt="Discussion"
                    className="mt-2 max-w-xs max-h-32 rounded-lg shadow-sm"
                  />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ====================================================================
// END Q&A DISCUSSION SYSTEM COMPONENTS
// ====================================================================

// ====================================================================
// ACTIVITY FEED COMPONENT
// ====================================================================

function ActivityFeed({ user }) {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchActivities(true);
  }, []);

  const fetchActivities = async (isInitial = false) => {
    const currentOffset = isInitial ? 0 : offset;
    setLoading(isInitial);
    
    try {
      const response = await apiCall(`/user/activity-feed?limit=20&offset=${currentOffset}`);
      const data = response.data;
      
      if (isInitial) {
        setActivities(data.activities);
        setOffset(20);
      } else {
        setActivities(prev => [...prev, ...data.activities]);
        setOffset(prev => prev + 20);
      }
      
      setHasMore(data.has_more);
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const refreshActivities = async () => {
    setRefreshing(true);
    await fetchActivities(true);
  };

  const getActivityIcon = (activityType) => {
    switch (activityType) {
      case 'quiz_published': return '📝';
      case 'question_posted': return '❓';
      case 'answer_posted': return '💬';
      case 'quiz_completed': return '🎯';
      case 'user_followed': return '👥';
      default: return '📰';
    }
  };

  const getActivityColor = (activityType) => {
    switch (activityType) {
      case 'quiz_published': return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
      case 'question_posted': return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      case 'answer_posted': return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'quiz_completed': return 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800';
      case 'user_followed': return 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800';
      default: return 'bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800';
    }
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInSeconds = Math.floor((now - time) / 1000);
    
    if (diffInSeconds < 60) return 'now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d`;
    return time.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const ActivityItem = ({ activity }) => (
    <AdminPostContainer
      isAdmin={activity.user_role === 'admin'}
      className={`border rounded-xl p-3 sm:p-4 mb-3 sm:mb-4 shadow-sm hover:shadow-md transition-shadow duration-200 ${
        activity.user_role !== 'admin' ? getActivityColor(activity.activity_type) : ''
      }`}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-start space-x-3">
          {/* Avatar/Icon - Optimized for mobile */}
          <div className="flex-shrink-0">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-sm border border-gray-200 dark:border-gray-600">
              <span className="text-lg sm:text-xl">{getActivityIcon(activity.activity_type)}</span>
            </div>
          </div>
          
          <div className="flex-1 min-w-0">
            {/* Header with timestamp - Mobile optimized */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm sm:text-base font-medium leading-snug">
                  <AdminName 
                    name={activity.user_name}
                    role={activity.user_role}
                    className="text-indigo-600 dark:text-indigo-400"
                  />
                  {activity.user_role === 'admin' && (
                    <AdminBadge size="default" className="ml-2" />
                  )}
                  </span>
                )}
                <span className="ml-1">{activity.title}</span>
              </p>
            </div>
            <div className="flex-shrink-0 ml-2">
              <span className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 font-medium bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full">
                {getTimeAgo(activity.created_at)}
              </span>
            </div>
          </div>
          
          {/* Description - Mobile friendly text */}
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mb-3 leading-relaxed break-words">
            {activity.description}
          </p>
          
          {/* Activity-specific metadata - Mobile optimized */}
          {activity.activity_type === 'quiz_published' && activity.metadata?.subject && (
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="inline-flex items-center px-2.5 py-1 bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 text-xs sm:text-sm rounded-full font-medium">
                📚 {activity.metadata.subject}
              </span>
              <span className="inline-flex items-center px-2.5 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs sm:text-sm rounded-full">
                {activity.metadata.total_questions} questions
              </span>
            </div>
          )}
          
          {activity.activity_type === 'quiz_completed' && activity.metadata?.score && (
            <div className="mb-3">
              <span className="inline-flex items-center px-3 py-1.5 bg-purple-100 dark:bg-purple-800 text-purple-800 dark:text-purple-200 text-sm font-semibold rounded-full">
                🏆 {activity.metadata.score}% Score
              </span>
            </div>
          )}
          
          {activity.activity_type === 'question_posted' && activity.metadata?.tags?.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 mb-3">
              {activity.metadata.tags.slice(0, 3).map((tag, index) => (
                <span key={index} className="inline-flex items-center px-2 py-1 bg-yellow-100 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200 text-xs rounded-full">
                  #{tag}
                </span>
              ))}
              {activity.metadata.tags.length > 3 && (
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  +{activity.metadata.tags.length - 3} more
                </span>
              )}
            </div>
          )}
          
          {activity.activity_type === 'answer_posted' && activity.metadata?.is_accepted && (
            <div className="mb-3">
              <span className="inline-flex items-center px-2.5 py-1 bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 text-xs sm:text-sm rounded-full font-medium">
                ✅ Accepted Answer
              </span>
            </div>
          )}
          
          {/* Action buttons - Mobile optimized touch targets */}
          {(activity.activity_type === 'quiz_published' || activity.activity_type === 'quiz_completed') && activity.related_id && (
            <div className="mt-3">
              <motion.button 
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-white dark:bg-gray-800 border border-indigo-200 dark:border-indigo-700 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors duration-200 min-h-[44px]"
              >
                <span className="mr-2">📝</span>
                View Quiz
              </motion.button>
            </div>
          )}
          
          {activity.activity_type === 'question_posted' && activity.related_id && (
            <div className="mt-3">
              <motion.button 
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-white dark:bg-gray-800 border border-indigo-200 dark:border-indigo-700 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors duration-200 min-h-[44px]"
              >
                <span className="mr-2">❓</span>
                View Question
              </motion.button>
            </div>
          )}
          
          {activity.activity_type === 'user_followed' && activity.related_id && (
            <div className="mt-3">
              <motion.button 
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-white dark:bg-gray-800 border border-indigo-200 dark:border-indigo-700 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors duration-200 min-h-[44px]"
              >
                <span className="mr-2">👤</span>
                View Profile
              </motion.button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );

  if (loading && activities.length === 0) {
    return (
      <PageTransition>
        <div className="max-w-4xl mx-auto px-2 sm:px-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
            <div className="flex items-center justify-center py-8 sm:py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              <span className="ml-3 text-gray-600 dark:text-gray-400 text-sm sm:text-base">Loading activities...</span>
            </div>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="max-w-4xl mx-auto px-2 sm:px-4">
        {/* Header - Mobile optimized */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-4 sm:mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <div className="flex-1">
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
                <span className="mr-2">📰</span>
                <span>Activity Feed</span>
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1 text-sm sm:text-base">
                Updates from people you follow
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={refreshActivities}
              disabled={refreshing}
              className="w-full sm:w-auto px-4 py-2.5 bg-indigo-600 dark:bg-indigo-500 text-white rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-600 transition duration-200 disabled:opacity-50 font-medium text-sm sm:text-base min-h-[44px] flex items-center justify-center"
            >
              <span className="mr-2">🔄</span>
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </motion.button>
          </div>
        </div>

        {/* Activity Feed - Mobile optimized */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-3 sm:p-6">
          {activities.length === 0 ? (
            <div className="text-center py-8 sm:py-12">
              <div className="text-4xl sm:text-6xl mb-4">👥</div>
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
                No activities yet
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm sm:text-base px-4">
                Start following other users to see their activities here
              </p>
              <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-500 bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mx-4">
                <p className="font-medium mb-1">You'll see activities like:</p>
                <div className="flex flex-wrap justify-center gap-2 text-xs">
                  <span className="px-2 py-1 bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 rounded">📝 Quiz publications</span>
                  <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200 rounded">❓ Q&A posts</span>
                  <span className="px-2 py-1 bg-purple-100 dark:bg-purple-800 text-purple-800 dark:text-purple-200 rounded">🎯 High scores</span>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Activity count - Mobile friendly */}
              <div className="mb-4 pb-3 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-200">
                    Recent Activities
                  </h2>
                  <span className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2.5 py-1 rounded-full">
                    {activities.length} {activities.length === 1 ? 'activity' : 'activities'}
                  </span>
                </div>
              </div>
              
              {/* Activities list */}
              <div className="space-y-0">
                {activities.map((activity) => (
                  <ActivityItem key={activity.id} activity={activity} />
                ))}
              </div>
              
              {/* Load more button - Mobile optimized */}
              {hasMore && (
                <div className="text-center mt-4 sm:mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => fetchActivities(false)}
                    disabled={loading}
                    className="w-full sm:w-auto px-6 py-3 bg-gray-600 dark:bg-gray-500 text-white rounded-lg hover:bg-gray-700 dark:hover:bg-gray-600 transition duration-200 disabled:opacity-50 font-medium text-sm sm:text-base min-h-[44px] flex items-center justify-center"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Loading...
                      </>
                    ) : (
                      <>
                        <span className="mr-2">📖</span>
                        Load More Activities
                      </>
                    )}
                  </motion.button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </PageTransition>
  );
}

// ====================================================================
// END ACTIVITY FEED COMPONENT
// ====================================================================

// ====================================================================
// USER PROFILE & NOTIFICATION SYSTEM COMPONENTS
// ====================================================================

// Notification Bell Component
const NotificationBell = ({ setCurrentView, currentView }) => {
  const [notificationCount, setNotificationCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetchNotificationCount();
    fetchRecentNotifications();
  }, []);

  const fetchNotificationCount = async () => {
    try {
      const response = await apiCall('/notifications/count');
      setNotificationCount(response.data.unread_count);
    } catch (error) {
      console.error('Error fetching notification count:', error);
    }
  };

  const fetchRecentNotifications = async () => {
    try {
      const response = await apiCall('/notifications?limit=5');
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await apiCall(`/notifications/${notificationId}/read`, { method: 'PUT' });
      await fetchNotificationCount();
      await fetchRecentNotifications();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  return (
    <div className="relative">
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className={`p-2 rounded-lg relative transition-colors ${
          currentView === 'notifications' 
            ? 'bg-indigo-600 dark:bg-indigo-500 text-white' 
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
        }`}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {notificationCount > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
          >
            {notificationCount > 9 ? '9+' : notificationCount}
          </motion.span>
        )}
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
          >
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-800 dark:text-gray-200">Bildirişlər</h3>
                <button
                  onClick={() => {
                    setCurrentView('notifications');
                    setIsOpen(false);
                  }}
                  className="text-indigo-600 dark:text-indigo-400 text-sm hover:underline"
                >
                  Hamısını gör
                </button>
              </div>
            </div>
            
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                  Bildirişiniz yoxdur
                </div>
              ) : (
                notifications.map((notification) => (
                  <motion.div
                    key={notification.id}
                    whileHover={{ backgroundColor: "rgba(99, 102, 241, 0.05)" }}
                    className={`p-3 border-b border-gray-100 dark:border-gray-700 cursor-pointer ${
                      !notification.is_read ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''
                    }`}
                    onClick={() => markAsRead(notification.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-indigo-100 dark:bg-indigo-800 rounded-full flex items-center justify-center">
                          {notification.type === 'new_answer' && '💬'}
                          {notification.type === 'answer_accepted' && '✅'}
                          {notification.type === 'quiz_result' && '📊'}
                          {notification.type === 'reply_to_answer' && '↩️'}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
                          {notification.title}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          {new Date(notification.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      {!notification.is_read && (
                        <div className="w-2 h-2 bg-indigo-500 rounded-full flex-shrink-0"></div>
                      )}
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Follow Button Component
const FollowButton = ({ userId, initialStats = null, className = '', onFollowChange = null }) => {
  const { currentUser } = useAuth();
  const [following, setFollowing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(initialStats);

  useEffect(() => {
    if (currentUser && userId && userId !== currentUser.id) {
      fetchFollowStatus();
    }
  }, [userId, currentUser]);

  const fetchFollowStatus = async () => {
    try {
      const response = await apiCall(`/users/${userId}/follow-stats`);
      setStats(response.data);
      setFollowing(response.data.is_following);
    } catch (error) {
      console.error('Error fetching follow status:', error);
    }
  };

  const handleFollowToggle = async () => {
    if (!currentUser || loading) return;
    
    setLoading(true);
    try {
      if (following) {
        await apiCall(`/follow/${userId}`, { method: 'DELETE' });
        setFollowing(false);
        if (stats) {
          setStats(prev => ({ ...prev, followers_count: prev.followers_count - 1, is_following: false }));
        }
      } else {
        await apiCall('/follow', {
          method: 'POST',
          data: { user_id: userId }
        });
        setFollowing(true);
        if (stats) {
          setStats(prev => ({ ...prev, followers_count: prev.followers_count + 1, is_following: true }));
        }
      }
      
      // Call callback if provided
      if (onFollowChange) {
        onFollowChange();
      }
    } catch (error) {
      console.error('Error toggling follow:', error);
      alert('Failed to update follow status: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  // Don't show button for current user's own profile
  if (!currentUser || !userId || userId === currentUser.id) {
    return null;
  }

  return (
    <button
      onClick={handleFollowToggle}
      disabled={loading}
      className={`px-4 py-2 rounded-lg font-semibold transition duration-200 ${
        following
          ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          : 'bg-blue-600 text-white hover:bg-blue-700'
      } ${loading ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {loading ? '⏳' : following ? '✅ Following' : '➕ Follow'}
    </button>
  );
};

// Enhanced User Profile Component with Admin Social Features
const UserProfile = ({ user, viewingUserId = null }) => {
  const { currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [userQuestions, setUserQuestions] = useState([]);
  const [userAnswers, setUserAnswers] = useState([]);
  const [userActivity, setUserActivity] = useState([]);
  const [userFollowers, setUserFollowers] = useState([]);
  const [userFollowing, setUserFollowing] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [isPrivateProfile, setIsPrivateProfile] = useState(false);
  const [canViewActivity, setCanViewActivity] = useState(true);

  // Determine which user profile to view (current user or specific user)
  const targetUserId = viewingUserId || user?.id;
  const isOwnProfile = targetUserId === currentUser?.id;
  const isAdminViewing = currentUser?.role === 'admin';

  useEffect(() => {
    if (targetUserId) {
      fetchProfile();
    }
  }, [targetUserId]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      let response;
      
      if (isOwnProfile) {
        response = await apiCall('/profile');
      } else {
        response = await apiCall(`/users/${targetUserId}/profile`);
      }
      
      setProfile(response.data);
      setIsPrivateProfile(response.data.is_private && !isOwnProfile && !isAdminViewing && !response.data.is_following);
      setCanViewActivity(response.data.can_view_activity);
      
      setEditData({
        name: response.data.name,
        bio: response.data.bio || '',
        location: response.data.location || '',
        website: response.data.website || ''
      });
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserActivity = async (type) => {
    if (!canViewActivity && !isAdminViewing && !isOwnProfile) {
      return;
    }

    try {
      let response;
      if (type === 'questions') {
        response = await apiCall(`/users/${targetUserId}/questions`);
        if (response.data.can_view !== false) {
          setUserQuestions(response.data.questions || []);
        }
      } else if (type === 'answers') {
        response = await apiCall(`/users/${targetUserId}/answers`);
        if (response.data.can_view !== false) {
          setUserAnswers(response.data.answers || []);
        }
      } else if (type === 'activity') {
        response = await apiCall(`/users/${targetUserId}/activity`);
        if (response.data.can_view !== false) {
          setUserActivity(response.data.activities || []);
        }
      } else if (type === 'followers') {
        response = await apiCall(`/users/${targetUserId}/followers`);
        if (response.data.can_view !== false) {
          setUserFollowers(response.data.followers || []);
        }
      } else if (type === 'following') {
        response = await apiCall(`/users/${targetUserId}/following`);
        if (response.data.can_view !== false) {
          setUserFollowing(response.data.following || []);
        }
      }
    } catch (error) {
      console.error(`Error fetching user ${type}:`, error);
    }
  };

  const updateProfile = async () => {
    if (!isOwnProfile) return;
    
    try {
      const response = await apiCall('/profile', {
        method: 'PUT',
        data: editData
      });
      setProfile(response.data);
      setEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setEditData({ ...editData, avatar: e.target.result });
      };
      reader.readAsDataURL(file);
    }
  };

  if (loading) {
    return (
      <PageTransition className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </PageTransition>
    );
  }

  // Private Profile View for Non-Followers
  if (isPrivateProfile && !canViewActivity) {
    return (
      <PageTransition className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-gray-500 to-gray-600 px-6 py-8">
            <div className="flex items-center space-x-6">
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center">
                {profile.avatar ? (
                  <img src={profile.avatar} alt="Avatar" className="w-20 h-20 rounded-full object-cover" />
                ) : (
                  <span className="text-2xl font-bold text-gray-600">
                    {profile.name.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h1 className="text-2xl font-bold text-white">{profile.name}</h1>
                  {profile.is_admin && (
                    <span className="bg-red-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                      {profile.admin_badge || '🛡️ Admin'}
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-4 mt-2 text-gray-100">
                  <span className="text-sm">🔒 This profile is private</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="p-6 text-center">
            <div className="text-6xl mb-4">🔒</div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
              Private Profile
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              This user has set their profile to private. Follow them to see their activity.
            </p>
            
            <div className="flex justify-center">
              <FollowButton 
                userId={targetUserId}
                onFollowChange={fetchProfile}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg"
              />
            </div>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition className="max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        {/* Profile Header */}
        <div className={`bg-gradient-to-r px-6 py-8 ${
          profile.is_admin 
            ? 'from-red-500 to-pink-600' 
            : 'from-indigo-500 to-purple-600'
        }`}>
          <div className="flex items-center space-x-6">
            <div className="relative">
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center">
                {profile.avatar ? (
                  <img src={profile.avatar} alt="Avatar" className="w-20 h-20 rounded-full object-cover" />
                ) : (
                  <span className="text-2xl font-bold text-indigo-600">
                    {profile.name.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              {editing && isOwnProfile && (
                <label className="absolute -bottom-2 -right-2 bg-indigo-600 text-white p-2 rounded-full cursor-pointer hover:bg-indigo-700">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
                </label>
              )}
            </div>
            
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    {editing && isOwnProfile ? (
                      <input
                        type="text"
                        value={editData.name}
                        onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                        className="text-2xl font-bold text-white bg-transparent border-b border-white/30 focus:border-white outline-none"
                      />
                    ) : (
                      <h1 className="text-2xl font-bold text-white">{profile.name}</h1>
                    )}
                    {profile.is_admin && (
                      <span className="bg-yellow-400 text-gray-800 px-3 py-1 rounded-full text-sm font-medium">
                        {profile.admin_badge || '🛡️ Admin'}
                      </span>
                    )}
                  </div>
                  
                  {(isOwnProfile || isAdminViewing) && profile.email && (
                    <p className="text-indigo-100">{profile.email}</p>
                  )}
                  
                  <div className="flex items-center space-x-4 mt-2 text-indigo-100">
                    <span className="text-sm">👤 {profile.role === 'admin' ? 'Admin' : 'User'}</span>
                    <span className="text-sm">📅 {new Date(profile.created_at).toLocaleDateString()}</span>
                    {profile.is_private && (
                      <span className="text-sm">🔒 Private</span>
                    )}
                  </div>
                </div>
                
                <div className="text-right">
                  {isOwnProfile ? (
                    editing ? (
                      <div className="space-x-2">
                        <button
                          onClick={updateProfile}
                          className="bg-white text-indigo-600 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          Save Changes
                        </button>
                        <button
                          onClick={() => setEditing(false)}
                          className="bg-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setEditing(true)}
                        className="bg-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-colors"
                      >
                        ✏️ Edit Profile
                      </button>
                    )
                  ) : (
                    <FollowButton 
                      userId={targetUserId}
                      onFollowChange={fetchProfile}
                      className="bg-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-colors"
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* Bio Section */}
          <div className="mt-4">
            {editing && isOwnProfile ? (
              <textarea
                value={editData.bio}
                onChange={(e) => setEditData({ ...editData, bio: e.target.value })}
                placeholder="Tell others about yourself..."
                className="w-full p-3 rounded-lg bg-white/20 text-white placeholder-white/70 resize-none"
                rows="3"
              />
            ) : (
              <p className="text-indigo-100">{profile.bio || 'No bio added yet'}</p>
            )}
          </div>
          
          {/* Location and Website */}
          {editing && isOwnProfile && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <input
                type="text"
                value={editData.location}
                onChange={(e) => setEditData({ ...editData, location: e.target.value })}
                placeholder="📍 Location"
                className="p-3 rounded-lg bg-white/20 text-white placeholder-white/70"
              />
              <input
                type="url"
                value={editData.website}
                onChange={(e) => setEditData({ ...editData, website: e.target.value })}
                placeholder="🌐 Website"
                className="p-3 rounded-lg bg-white/20 text-white placeholder-white/70"
              />
            </div>
          )}
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{profile.questions_count || 0}</div>
              <div className="text-indigo-100 text-sm">Questions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{profile.answers_count || 0}</div>
              <div className="text-indigo-100 text-sm">Answers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{profile.accepted_answers || 0}</div>
              <div className="text-indigo-100 text-sm">Accepted</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{profile.quizzes_taken || 0}</div>
              <div className="text-indigo-100 text-sm">Quizzes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{profile.follower_count || 0}</div>
              <div className="text-indigo-100 text-sm">Followers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{profile.following_count || 0}</div>
              <div className="text-indigo-100 text-sm">Following</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-4 px-6 overflow-x-auto">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'questions', label: 'Questions', icon: '❓' },
              { id: 'answers', label: 'Answers', icon: '💬' },
              { id: 'activity', label: 'Activity', icon: '📈' },
              { id: 'followers', label: 'Followers', icon: '👥' },
              { id: 'following', label: 'Following', icon: '👤' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  if (tab.id !== 'overview') fetchUserActivity(tab.id);
                }}
                className={`py-4 px-2 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-4">Q&A Activity</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Questions:</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-200">{profile.questions_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Answers:</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-200">{profile.answers_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Accepted answers:</span>
                    <span className="font-semibold text-green-600">{profile.accepted_answers || 0}</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-4">Quiz Statistics</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Quizzes taken:</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-200">{profile.quizzes_taken || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Average score:</span>
                    <span className="font-semibold text-blue-600">{profile.avg_quiz_score || 0}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total score:</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-200">{(profile.total_quiz_score || 0).toFixed(1)}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'questions' && (
            <div className="space-y-4">
              {userQuestions.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No questions posted yet
                </div>
              ) : (
                userQuestions.map((question) => (
                  <div key={question.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">{question.title}</h4>
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">{question.content?.substring(0, 150)}...</p>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <div className="flex items-center space-x-4">
                            <span>👍 {question.upvotes || 0}</span>
                            <span>💬 {question.answer_count || 0} answers</span>
                            {question.subject && (
                              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                {question.subject}
                              </span>
                            )}
                          </div>
                          <span>{new Date(question.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'answers' && (
            <div className="space-y-4">
              {userAnswers.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No answers posted yet
                </div>
              ) : (
                userAnswers.map((answer) => (
                  <div key={answer.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className="flex-1">
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">{answer.content?.substring(0, 200)}...</p>
                        {answer.question && (
                          <p className="text-xs text-indigo-600 dark:text-indigo-400 mb-2">
                            Question: {answer.question.title}
                          </p>
                        )}
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>👍 {answer.upvotes || 0}</span>
                          <span>{new Date(answer.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      {answer.is_accepted && (
                        <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                          ✅ Accepted
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'activity' && (
            <div className="space-y-4">
              {userActivity.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No recent activity
                </div>
              ) : (
                userActivity.map((activity, index) => (
                  <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className="text-2xl">
                        {activity.type === 'question_posted' ? '❓' : 
                         activity.type === 'answer_posted' ? '💬' : 
                         activity.type === 'quiz_completed' ? '🏆' : '📝'}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">{activity.title}</h4>
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">{activity.content}</p>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <div className="flex items-center space-x-2">
                            {activity.upvotes && <span>👍 {activity.upvotes}</span>}
                            {activity.score && <span>🎯 {activity.score.toFixed(1)}%</span>}
                            {activity.subject && (
                              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                {activity.subject}
                              </span>
                            )}
                          </div>
                          <span>{new Date(activity.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'followers' && (
            <div className="space-y-4">
              {userFollowers.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No followers yet
                </div>
              ) : (
                userFollowers.map((follower) => (
                  <div key={follower.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                        {follower.avatar ? (
                          <img src={follower.avatar} alt="Avatar" className="w-12 h-12 rounded-full object-cover" />
                        ) : (
                          <span className="text-lg font-bold text-indigo-600">
                            {follower.name.charAt(0).toUpperCase()}
                          </span>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-semibold text-gray-800 dark:text-gray-200">{follower.name}</h4>
                          {follower.is_admin && (
                            <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">
                              {follower.admin_badge || '🛡️ Admin'}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">
                          Followed: {new Date(follower.followed_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'following' && (
            <div className="space-y-4">
              {userFollowing.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  Not following anyone yet
                </div>
              ) : (
                userFollowing.map((following) => (
                  <div key={following.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                        {following.avatar ? (
                          <img src={following.avatar} alt="Avatar" className="w-12 h-12 rounded-full object-cover" />
                        ) : (
                          <span className="text-lg font-bold text-indigo-600">
                            {following.name.charAt(0).toUpperCase()}
                          </span>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-semibold text-gray-800 dark:text-gray-200">{following.name}</h4>
                          {following.is_admin && (
                            <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">
                              {following.admin_badge || '🛡️ Admin'}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">
                          Following since: {new Date(following.followed_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <FollowButton 
                          userId={following.id}
                          onFollowChange={() => fetchUserActivity('following')}
                          className="text-xs px-3 py-1"
                        />
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};


// Notification Center Component
const NotificationCenter = ({ user }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const unreadOnly = filter === 'unread';
      const response = await apiCall(`/notifications?unread_only=${unreadOnly}&limit=50`);
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await apiCall(`/notifications/${notificationId}/read`, { method: 'PUT' });
      await fetchNotifications();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await apiCall('/notifications/mark-all-read', { method: 'PUT' });
      await fetchNotifications();
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      await apiCall(`/notifications/${notificationId}`, { method: 'DELETE' });
      await fetchNotifications();
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const getNotificationIcon = (type) => {
    const iconMap = {
      new_answer: '💬',
      answer_accepted: '✅',
      reply_to_answer: '↩️',
      quiz_result: '📊',
      leaderboard_update: '🏆',
      question_vote: '👍',
      answer_vote: '❤️'
    };
    return iconMap[type] || '📢';
  };

  const getNotificationColor = (type) => {
    const colorMap = {
      new_answer: 'blue',
      answer_accepted: 'green',
      reply_to_answer: 'purple',
      quiz_result: 'indigo',
      leaderboard_update: 'yellow',
      question_vote: 'pink',
      answer_vote: 'red'
    };
    return colorMap[type] || 'gray';
  };

  if (loading) {
    return (
      <PageTransition className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </PageTransition>
    );
  }

  return (
    <PageTransition className="max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">🔔 Bildirişlər</h1>
              <p className="text-indigo-100">Fəaliyyətləriniz haqqında yeniliklər</p>
            </div>
            <button
              onClick={markAllAsRead}
              className="bg-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-colors"
            >
              Hamısını oxunmuş kimi qeyd et
            </button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'all', label: 'Hamısı' },
              { id: 'unread', label: 'Oxunmamış' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  filter === tab.id
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Notifications List */}
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {notifications.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔕</div>
              <p className="text-gray-500 dark:text-gray-400 text-lg">
                {filter === 'unread' ? 'Oxunmamış bildirişiniz yoxdur' : 'Bildirişiniz yoxdur'}
              </p>
            </div>
          ) : (
            notifications.map((notification) => {
              const color = getNotificationColor(notification.type);
              return (
                <motion.div
                  key={notification.id}
                  whileHover={{ backgroundColor: "rgba(99, 102, 241, 0.02)" }}
                  className={`p-6 ${!notification.is_read ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''}`}
                >
                  <div className="flex items-start space-x-4">
                    <div className={`flex-shrink-0 w-12 h-12 bg-${color}-100 dark:bg-${color}-800 rounded-full flex items-center justify-center`}>
                      <span className="text-xl">{getNotificationIcon(notification.type)}</span>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-lg font-medium text-gray-800 dark:text-gray-200">
                          {notification.title}
                        </p>
                        <div className="flex items-center space-x-2">
                          {!notification.is_read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 text-sm"
                            >
                              Oxunmuş
                            </button>
                          )}
                          <button
                            onClick={() => deleteNotification(notification.id)}
                            className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm"
                          >
                            Sil
                          </button>
                        </div>
                      </div>
                      
                      <p className="text-gray-600 dark:text-gray-400 mt-1">
                        {notification.message}
                      </p>
                      
                      <div className="flex items-center justify-between mt-3">
                        <span className="text-sm text-gray-500 dark:text-gray-500">
                          {new Date(notification.created_at).toLocaleString()}
                        </span>
                        {!notification.is_read && (
                          <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </div>
    </PageTransition>
  );
};

// ====================================================================
// END USER PROFILE & NOTIFICATION SYSTEM COMPONENTS
// ====================================================================

export default App;