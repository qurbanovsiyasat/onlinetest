import { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}

function MainApp() {
  const { user, loading } = useAuth();
  const [currentView, setCurrentView] = useState('home');

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
      alert(`Admin created successfully!\nEmail: admin@onlinetestmaker.com\nPassword: admin123`);
    } catch (error) {
      alert(error.response?.data?.detail || 'Admin already exists or error occurred');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">📝 OnlineTestMaker</h1>
          <p className="text-gray-600">Admin-Controlled Quiz Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Full Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter your full name"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div className={`p-3 rounded-lg ${error.includes('successful') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold disabled:opacity-50"
          >
            {loading ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
              setFormData({ name: '', email: '', password: '' });
            }}
            className="text-indigo-600 hover:text-indigo-800 font-semibold"
          >
            {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
          </button>
        </div>

        <div className="mt-4 text-center">
          <button
            onClick={initializeAdmin}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Initialize Admin User
          </button>
        </div>
      </div>
    </div>
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
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">👑 Admin Dashboard</h1>
            <p className="text-gray-600">Welcome back, {user.name}</p>
          </div>
          <button
            onClick={logout}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
          >
            Logout
          </button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-wrap gap-4 mb-8">
          <button
            onClick={() => setCurrentView('dashboard')}
            className={`px-6 py-3 rounded-lg font-semibold transition duration-200 ${
              currentView === 'dashboard' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            📊 Dashboard
          </button>
          <button
            onClick={() => setCurrentView('users')}
            className={`px-6 py-3 rounded-lg font-semibold transition duration-200 ${
              currentView === 'users' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            👥 Users
          </button>
          <button
            onClick={() => setCurrentView('quizzes')}
            className={`px-6 py-3 rounded-lg font-semibold transition duration-200 ${
              currentView === 'quizzes' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            📝 Quizzes
          </button>
          <button
            onClick={() => setCurrentView('results')}
            className={`px-6 py-3 rounded-lg font-semibold transition duration-200 ${
              currentView === 'results' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            📈 Test Results
          </button>
          <button
            onClick={() => setCurrentView('categories')}
            className={`px-6 py-3 rounded-lg font-semibold transition duration-200 ${
              currentView === 'categories' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            🗂️ Categories
          </button>
          <button
            onClick={() => setCurrentView('create-quiz')}
            className={`px-6 py-3 rounded-lg font-semibold transition duration-200 ${
              currentView === 'create-quiz' ? 'bg-green-600 text-white' : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            ➕ Create Quiz
          </button>
        </div>

        {/* Content */}
        {currentView === 'dashboard' && <AdminDashboardHome analytics={analytics} />}
        {currentView === 'users' && <AdminUsersView users={users} />}
        {currentView === 'quizzes' && <AdminQuizzesView quizzes={quizzes} fetchQuizzes={fetchQuizzes} />}
        {currentView === 'results' && <AdminResultsView results={quizResults} />}
        {currentView === 'categories' && <AdminCategoriesView categories={categories} fetchCategories={fetchCategories} />}
        {currentView === 'create-quiz' && <AdminCreateQuiz setCurrentView={setCurrentView} />}
      </div>
    </div>
  );
}

// Admin Dashboard Components
function AdminDashboardHome({ analytics }) {
  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 text-blue-600">
              👥
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Users</h3>
              <p className="text-2xl font-semibold text-gray-900">{analytics.total_users || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 text-green-600">
              📝
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Quizzes</h3>
              <p className="text-2xl font-semibold text-gray-900">{analytics.total_quizzes || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100 text-purple-600">
              📊
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Attempts</h3>
              <p className="text-2xl font-semibold text-gray-900">{analytics.total_attempts || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100 text-yellow-600">
              🎯
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Average Score</h3>
              <p className="text-2xl font-semibold text-gray-900">{analytics.average_score || 0}%</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">📈 Platform Overview</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Most Popular Quiz:</span>
              <span className="font-medium">{analytics.most_popular_quiz || 'None'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Platform Status:</span>
              <span className="text-green-600 font-medium">Active</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">🚀 Quick Actions</h3>
          <div className="space-y-2">
            <p className="text-gray-600">• Create new quizzes and manage content</p>
            <p className="text-gray-600">• View detailed user test results</p>
            <p className="text-gray-600">• Manage user accounts and permissions</p>
            <p className="text-gray-600">• Organize quizzes by categories</p>
          </div>
        </div>
      </div>
    </div>
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
    if (percentage >= 80) return 'Excellent';
    if (percentage >= 60) return 'Good';
    return 'Needs Improvement';
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
        <h3 className="font-semibold text-gray-800 mb-2">📊 Summary Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Total Results:</p>
            <p className="font-semibold">{filteredAndSortedResults.length}</p>
          </div>
          <div>
            <p className="text-gray-600">High Scores (80%+):</p>
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

  useEffect(() => {
    if (viewMode === 'folders') {
      fetchSubjectsStructure();
    }
  }, [viewMode]);

  const fetchSubjectsStructure = async () => {
    try {
      const response = await apiCall('/admin/subjects-structure');
      setSubjectsStructure(response.data);
    } catch (error) {
      console.error('Error fetching subjects structure:', error);
    }
  };

  const deleteQuiz = async (quizId) => {
    if (window.confirm('Are you sure you want to delete this quiz?')) {
      try {
        await apiCall(`/admin/quiz/${quizId}`, { method: 'DELETE' });
        fetchQuizzes();
        if (viewMode === 'folders') {
          fetchSubjectsStructure();
        }
      } catch (error) {
        alert('Error deleting quiz');
      }
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

  const QuizCard = ({ quiz, showSubject = true }) => (
    <div className="border rounded-lg p-4 relative">
      <div className="mb-2 flex flex-wrap gap-1">
        <span className={`inline-block px-2 py-1 rounded text-xs ${
          quiz.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {quiz.is_public ? 'Public' : 'Private'}
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
      
      <div className="flex gap-1 text-xs">
        <button
          onClick={() => editQuiz(quiz)}
          className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition duration-200"
        >
          ✏️ Edit
        </button>
        <button
          onClick={() => toggleQuizVisibility(quiz)}
          className={`flex-1 py-2 rounded transition duration-200 ${
            quiz.is_public 
              ? 'bg-yellow-600 text-white hover:bg-yellow-700' 
              : 'bg-green-600 text-white hover:bg-green-700'
          }`}
        >
          {quiz.is_public ? '🔒 Private' : '🔓 Public'}
        </button>
        <button
          onClick={() => deleteQuiz(quiz.id)}
          className="flex-1 bg-red-600 text-white py-2 rounded hover:bg-red-700 transition duration-200"
        >
          🗑️ Delete
        </button>
      </div>
    </div>
  );

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
    </div>
  );
}

function QuizEditModal({ quiz, onClose, onUpdate }) {
  const [editData, setEditData] = useState({
    title: quiz.title,
    description: quiz.description,
    category: quiz.category,
    subject: quiz.subject || 'Mathematics',
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

  const removeQuestion = (questionIndex) => {
    if (confirm('Are you sure you want to remove this question?')) {
      const updatedQuestions = editData.questions.filter((_, index) => index !== questionIndex);
      setEditData({ ...editData, questions: updatedQuestions });
      setEditingQuestionIndex(null);
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
      </div>
    </div>
  );
}

function AdminCategoriesView({ categories, fetchCategories }) {
  const [newCategory, setNewCategory] = useState({ name: '', description: '' });
  const [subjectFolders, setSubjectFolders] = useState([]);
  const [newFolder, setNewFolder] = useState({ 
    name: '', 
    description: '', 
    is_visible: true, 
    allowed_users: [] 
  });
  const [allUsers, setAllUsers] = useState([]);
  const [activeTab, setActiveTab] = useState('categories'); // 'categories' or 'folders'

  useEffect(() => {
    if (activeTab === 'folders') {
      fetchSubjectFolders();
      fetchAllUsers();
    }
  }, [activeTab]);

  const fetchSubjectFolders = async () => {
    try {
      const response = await apiCall('/admin/subject-folders');
      setSubjectFolders(response.data);
    } catch (error) {
      console.error('Error fetching subject folders:', error);
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

  const createCategory = async () => {
    if (!newCategory.name) return;
    
    try {
      await apiCall('/admin/category', {
        method: 'POST',
        params: { category_name: newCategory.name, description: newCategory.description }
      });
      setNewCategory({ name: '', description: '' });
      fetchCategories();
    } catch (error) {
      alert('Error creating category');
    }
  };

  const createSubjectFolder = async () => {
    if (!newFolder.name) {
      alert('Folder name is required');
      return;
    }
    
    try {
      await apiCall('/admin/subject-folder', {
        method: 'POST',
        data: newFolder
      });
      setNewFolder({ name: '', description: '', is_visible: true, allowed_users: [] });
      fetchSubjectFolders();
      alert('Subject folder created successfully!');
    } catch (error) {
      alert('Error creating subject folder: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const toggleFolderVisibility = async (folderId, currentVisibility) => {
    try {
      await apiCall(`/admin/subject-folder/${folderId}`, {
        method: 'PUT',
        data: { is_visible: !currentVisibility }
      });
      fetchSubjectFolders();
    } catch (error) {
      alert('Error updating folder visibility');
    }
  };

  const deleteFolder = async (folderId, folderName) => {
    if (window.confirm(`Are you sure you want to delete the folder "${folderName}"? This action cannot be undone.`)) {
      try {
        await apiCall(`/admin/subject-folder/${folderId}`, {
          method: 'DELETE'
        });
        fetchSubjectFolders();
        alert('Folder deleted successfully!');
      } catch (error) {
        alert('Error deleting folder: ' + (error.response?.data?.detail || 'Unknown error'));
      }
    }
  };

  const toggleUserAccessForFolder = (userId) => {
    setNewFolder({
      ...newFolder,
      allowed_users: newFolder.allowed_users.includes(userId)
        ? newFolder.allowed_users.filter(id => id !== userId)
        : [...newFolder.allowed_users, userId]
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Tabs */}
      <div className="flex mb-6">
        <button
          onClick={() => setActiveTab('categories')}
          className={`px-4 py-2 rounded-l-lg transition duration-200 ${
            activeTab === 'categories' 
              ? 'bg-indigo-600 text-white' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          📝 Quiz Categories
        </button>
        <button
          onClick={() => setActiveTab('folders')}
          className={`px-4 py-2 rounded-r-lg transition duration-200 ${
            activeTab === 'folders' 
              ? 'bg-indigo-600 text-white' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          📁 Subject Folders
        </button>
      </div>

      {activeTab === 'categories' ? (
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Quiz Categories</h2>
          
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-3">Create New Category</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Category name"
                value={newCategory.name}
                onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                className="p-2 border border-gray-300 rounded"
              />
              <input
                type="text"
                placeholder="Description (optional)"
                value={newCategory.description}
                onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                className="p-2 border border-gray-300 rounded"
              />
            </div>
            <button
              onClick={createCategory}
              className="mt-3 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition duration-200"
            >
              Create Category
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((category) => (
              <div key={category.id} className="border rounded-lg p-4">
                <h3 className="font-semibold text-gray-800">{category.name}</h3>
                <p className="text-gray-600 text-sm">{category.description || 'No description'}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Subject Folder Management</h2>
          
          {/* Create New Folder */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-3">Create New Subject Folder</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Folder name (e.g., Mathematics)"
                  value={newFolder.name}
                  onChange={(e) => setNewFolder({ ...newFolder, name: e.target.value })}
                  className="p-2 border border-gray-300 rounded"
                />
                <input
                  type="text"
                  placeholder="Description (optional)"
                  value={newFolder.description}
                  onChange={(e) => setNewFolder({ ...newFolder, description: e.target.value })}
                  className="p-2 border border-gray-300 rounded"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={newFolder.is_visible}
                  onChange={(e) => setNewFolder({ ...newFolder, is_visible: e.target.checked })}
                  className="mr-2"
                />
                <label>Visible to Users</label>
              </div>

              {newFolder.is_visible && (
                <div>
                  <label className="block text-gray-700 font-semibold mb-2">
                    Select Users with Access ({newFolder.allowed_users.length} selected)
                  </label>
                  <div className="max-h-32 overflow-y-auto border border-gray-300 rounded-lg p-3">
                    {allUsers.map((user) => (
                      <div key={user.id} className="flex items-center mb-2">
                        <input
                          type="checkbox"
                          checked={newFolder.allowed_users.includes(user.id)}
                          onChange={() => toggleUserAccessForFolder(user.id)}
                          className="mr-3"
                        />
                        <span className="text-sm">{user.name} ({user.email})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <button
              onClick={createSubjectFolder}
              className="mt-3 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition duration-200"
            >
              ➕ Create Subject Folder
            </button>
          </div>

          {/* Existing Folders */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {subjectFolders.map((folder) => (
              <div key={folder.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-800">{folder.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs ${
                    folder.is_visible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {folder.is_visible ? 'Visible' : 'Hidden'}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-3">
                  {folder.description || 'No description'}
                </p>
                
                {folder.allowed_users && folder.allowed_users.length > 0 && (
                  <p className="text-xs text-blue-600 mb-3">
                    {folder.allowed_users.length} users have access
                  </p>
                )}
                
                <div className="flex gap-2">
                  <button
                    onClick={() => toggleFolderVisibility(folder.id, folder.is_visible)}
                    className={`flex-1 py-1 px-2 rounded text-xs transition duration-200 ${
                      folder.is_visible 
                        ? 'bg-yellow-600 text-white hover:bg-yellow-700' 
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {folder.is_visible ? '👁️ Hide' : '👀 Show'}
                  </button>
                  <button
                    onClick={() => deleteFolder(folder.id, folder.name)}
                    className="flex-1 py-1 px-2 rounded text-xs bg-red-600 text-white hover:bg-red-700 transition duration-200"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
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
    subject: 'Mathematics',
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

  useEffect(() => {
    fetchPredefinedSubjects();
    if (quiz.is_public) {
      fetchAllUsers();
    }
  }, [quiz.is_public]);

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
    
    if (!quiz.title || quiz.title.length < 3) {
      errors.push('Title must be at least 3 characters long');
    }
    
    if (!quiz.description || quiz.description.length < 10) {
      errors.push('Description must be at least 10 characters long');
    }
    
    if (!quiz.category || quiz.category.length < 2) {
      errors.push('Category is required');
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
      alert('Quiz created successfully as draft!');
      setCurrentView('quizzes');
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

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Create Advanced Quiz</h2>
      
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
            <select
              value={quiz.subject}
              onChange={(e) => setQuiz({ ...quiz, subject: e.target.value, subcategory: 'General' })}
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
              value={quiz.subcategory}
              onChange={(e) => setQuiz({ ...quiz, subcategory: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
            >
              {getSubcategories().map(subcategory => (
                <option key={subcategory} value={subcategory}>{subcategory}</option>
              ))}
            </select>
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
                <QuestionPreview key={index} question={question} index={index} />
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
    setCurrentView('take-quiz');
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
    try {
      const response = await apiCall(`/quiz/${selectedQuiz.id}/attempt`, {
        method: 'POST',
        data: {
          quiz_id: selectedQuiz.id,
          answers: userAnswers
        }
      });
      setQuizResult(response.data);
      setCurrentView('result');
    } catch (error) {
      alert('Error submitting quiz: ' + (error.response?.data?.detail || 'Unknown error'));
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
      setCurrentView={setCurrentView}
    />;
  }

  if (currentView === 'result') {
    return <UserResult 
      result={quizResult}
      quiz={selectedQuiz}
      setCurrentView={setCurrentView}
      startQuiz={startQuiz}
    />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">📝 OnlineTestMaker</h1>
            <p className="text-gray-600">Welcome, {user.name}</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => setCurrentView('home')}
              className={`px-4 py-2 rounded-lg transition duration-200 ${
                currentView === 'home' ? 'bg-indigo-600 text-white' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              🏠 Home
            </button>
            <button
              onClick={() => setCurrentView('my-attempts')}
              className={`px-4 py-2 rounded-lg transition duration-200 ${
                currentView === 'my-attempts' ? 'bg-indigo-600 text-white' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              📊 My Results
            </button>
            <button
              onClick={() => setShowPasswordChange(true)}
              className="text-gray-700 hover:bg-gray-100 px-4 py-2 rounded-lg transition duration-200"
            >
              🔑 Change Password
            </button>
            <button
              onClick={logout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {currentView === 'home' && (
          <div>
            <h2 className="text-3xl font-bold text-gray-800 mb-6">Available Quizzes</h2>
            {quizzes.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No quizzes available yet.</p>
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {quizzes.map((quiz) => (
                  <div key={quiz.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200">
                    <div className="mb-2 flex flex-wrap gap-1">
                      <span className="inline-block bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                        {quiz.subject || 'General'}
                      </span>
                      <span className="inline-block bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">
                        {quiz.subcategory || 'General'}
                      </span>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">{quiz.title}</h3>
                    <p className="text-gray-600 mb-4">{quiz.description}</p>
                    <div className="flex justify-between items-center mb-4 text-sm text-gray-500">
                      <span>{quiz.total_questions} questions</span>
                      <span>{quiz.total_attempts || 0} attempts</span>
                    </div>
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-sm text-gray-500">
                        Category: {quiz.category}
                      </span>
                      <span className="text-sm text-gray-500">
                        Avg: {quiz.average_score || 0}%
                      </span>
                    </div>
                    <button
                      onClick={() => startQuiz(quiz)}
                      className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
                    >
                      🎯 Take Quiz
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {currentView === 'my-attempts' && (
          <div>
            <h2 className="text-3xl font-bold text-gray-800 mb-6">My Quiz Results</h2>
            {myAttempts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">You haven't taken any quizzes yet.</p>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {myAttempts.map((attempt) => (
                  <div key={attempt.id} className="bg-white rounded-lg shadow p-6">
                    <h3 className="font-semibold text-gray-800 mb-2">Quiz Attempt</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Score:</span>
                        <span className="font-semibold">{attempt.score}/{attempt.total_questions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Percentage:</span>
                        <span className={`font-semibold ${
                          attempt.percentage >= 80 ? 'text-green-600' :
                          attempt.percentage >= 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {attempt.percentage.toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Date:</span>
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
    </div>
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
  return (
    <div className="bg-gray-50 p-6 rounded-lg mb-6">
      <h3 className="text-lg font-semibold mb-4">Add Question</h3>
      
      {/* Question Type Selection */}
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">Question Type</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="questionType"
              value="multiple_choice"
              checked={currentQuestion.question_type === 'multiple_choice'}
              onChange={(e) => setCurrentQuestion({ ...currentQuestion, question_type: e.target.value })}
              className="mr-2"
            />
            📝 Multiple Choice
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

      {/* Question Text */}
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">Question Text *</label>
        <textarea
          value={currentQuestion.question_text}
          onChange={(e) => setCurrentQuestion({ ...currentQuestion, question_text: e.target.value })}
          className="w-full p-3 border border-gray-300 rounded-lg"
          rows="2"
          placeholder="Enter your question (min 5 characters)"
        />
      </div>

      {/* Question Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div>
          <label className="block text-gray-700 font-semibold mb-2">Points</label>
          <input
            type="number"
            min="1"
            max="10"
            value={currentQuestion.points}
            onChange={(e) => setCurrentQuestion({ ...currentQuestion, points: parseInt(e.target.value) || 1 })}
            className="w-full p-3 border border-gray-300 rounded-lg"
          />
        </div>
        
        <div>
          <label className="block text-gray-700 font-semibold mb-2">Difficulty</label>
          <select
            value={currentQuestion.difficulty}
            onChange={(e) => setCurrentQuestion({ ...currentQuestion, difficulty: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg"
          >
            <option value="easy">🟢 Easy</option>
            <option value="medium">🟡 Medium</option>
            <option value="hard">🔴 Hard</option>
          </select>
        </div>
        
        <div className="flex items-center pt-8">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={currentQuestion.is_mandatory}
              onChange={(e) => setCurrentQuestion({ ...currentQuestion, is_mandatory: e.target.checked })}
              className="mr-2"
            />
            Mandatory
          </label>
        </div>

        {currentQuestion.question_type === 'multiple_choice' && (
          <div className="flex items-center pt-8">
            <label className="flex items-center">
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Image Upload */}
        <div>
          <label className="block text-gray-700 font-semibold mb-2">Question Image</label>
          {!currentQuestion.image_url ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileUpload(e, 'image')}
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
                {uploadingFile ? 'Uploading...' : '📷 Upload Image'}
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
        <label className="block text-gray-700 font-semibold mb-2">Explanation (Optional)</label>
        <textarea
          value={currentQuestion.explanation}
          onChange={(e) => setCurrentQuestion({ ...currentQuestion, explanation: e.target.value })}
          className="w-full p-3 border border-gray-300 rounded-lg"
          rows="2"
          placeholder="Explain the answer or provide additional context"
        />
      </div>

      <button
        onClick={addQuestion}
        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
      >
        ➕ Add Question
      </button>
    </div>
  );
}

function MultipleChoiceQuestionForm({ currentQuestion, addOption, removeOption, updateOption }) {
  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-gray-700 font-semibold">Options *</label>
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
      
      <div className="space-y-2">
        {currentQuestion.options.map((option, index) => (
          <div key={index} className="flex items-center gap-2">
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
              onChange={(e) => updateOption(index, 'text', e.target.value)}
              className="flex-1 p-2 border border-gray-300 rounded-lg"
              placeholder={`Option ${String.fromCharCode(65 + index)}`}
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

function QuestionPreview({ question, index }) {
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
          Question {index + 1}: {question.question_text}
        </h4>
        <div className="flex gap-2">
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
                {String.fromCharCode(65 + optIndex)}. {option.text}
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
          <h3 className="text-lg font-semibold">Change Password</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Current Password</label>
            <input
              type="password"
              value={formData.current_password}
              onChange={(e) => setFormData({ ...formData, current_password: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">New Password</label>
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
            <label className="block text-gray-700 font-semibold mb-2">Confirm New Password</label>
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
              {loading ? 'Changing...' : 'Change Password'}
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
      </div>
    </div>
  );
}

// User Quiz Taking Components
function UserTakeQuiz({ quiz, currentQuestionIndex, setCurrentQuestionIndex, userAnswers, selectAnswer, nextQuestion, setCurrentView }) {
  if (!quiz) return null;

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;

  const handleMultipleChoiceSelect = (optionText) => {
    if (currentQuestion.multiple_correct) {
      // Handle multiple correct answers
      const currentAnswers = userAnswers[currentQuestionIndex] ? 
        userAnswers[currentQuestionIndex].split(', ').filter(a => a) : [];
      
      if (currentAnswers.includes(optionText)) {
        // Remove if already selected
        const newAnswers = currentAnswers.filter(a => a !== optionText);
        selectAnswer(newAnswers.join(', '));
      } else {
        // Add to selected answers
        selectAnswer([...currentAnswers, optionText].join(', '));
      }
    } else {
      // Single correct answer
      selectAnswer(optionText);
    }
  };

  const handleOpenEndedInput = (value) => {
    selectAnswer(value);
  };

  const isOptionSelected = (optionText) => {
    const currentAnswer = userAnswers[currentQuestionIndex] || '';
    if (currentQuestion.multiple_correct) {
      return currentAnswer.split(', ').includes(optionText);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <button
            onClick={() => setCurrentView('home')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 font-semibold"
          >
            ← Back to Home
          </button>
          <h1 className="text-4xl font-bold text-teal-900 mb-2">{quiz.title}</h1>
          <p className="text-gray-600 mb-4">{quiz.description}</p>
          
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div
              className="bg-teal-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600">
            Question {currentQuestionIndex + 1} of {quiz.questions.length}
          </p>
        </header>

        <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-lg p-8">
          {/* Question Header */}
          <div className="flex justify-between items-start mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-2xl">{getQuestionTypeIcon(currentQuestion.question_type)}</span>
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
              <h2 className="text-2xl font-semibold text-gray-800">
                {currentQuestion.question_text}
              </h2>
            </div>
          </div>

          {/* Media Display */}
          <div className="flex gap-4 mb-6">
            {currentQuestion.image_url && (
              <div className="mb-6">
                <img
                  src={currentQuestion.image_url}
                  alt="Question"
                  className="max-w-full h-auto rounded-lg shadow"
                />
              </div>
            )}
            {currentQuestion.pdf_url && (
              <div className="mb-6">
                <div className="border-2 border-dashed border-red-300 rounded-lg p-6 text-center bg-red-50">
                  <div className="text-4xl mb-2">📄</div>
                  <p className="text-red-700 font-medium">PDF Attachment Available</p>
                  <a
                    href={currentQuestion.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition duration-200"
                  >
                    View PDF
                  </a>
                </div>
              </div>
            )}
          </div>

          {/* Question Content Based on Type */}
          <div className="mb-8">
            {currentQuestion.question_type === 'multiple_choice' ? (
              <div className="space-y-4">
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
                    className={`w-full p-4 text-left rounded-lg border-2 transition duration-200 ${
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
                      <span className="font-semibold mr-3">{String.fromCharCode(65 + index)}.</span>
                      <span className="flex-1">{option.text}</span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-3 bg-yellow-50 rounded-lg mb-4">
                  <p className="text-yellow-800 text-sm font-medium">
                    ✏️ Open-ended question. Type your answer in the text area below.
                  </p>
                </div>
                
                <textarea
                  value={userAnswers[currentQuestionIndex] || ''}
                  onChange={(e) => handleOpenEndedInput(e.target.value)}
                  className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:outline-none resize-y min-h-32"
                  placeholder="Type your answer here..."
                  rows="4"
                />
                
                <div className="text-sm text-gray-500">
                  {userAnswers[currentQuestionIndex]?.length || 0} characters
                </div>
              </div>
            )}
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <button
              onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
              disabled={currentQuestionIndex === 0}
              className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <button
              onClick={nextQuestion}
              disabled={!userAnswers[currentQuestionIndex] || 
                       (userAnswers[currentQuestionIndex] && userAnswers[currentQuestionIndex].trim() === '')}
              className="px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              {currentQuestionIndex === quiz.questions.length - 1 ? 'Submit Quiz' : 'Next Question'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function UserResult({ result, quiz, setCurrentView, startQuiz }) {
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
    if (percentage >= 80) return { text: 'Excellent!', color: 'bg-green-500' };
    if (percentage >= 60) return { text: 'Good Job!', color: 'bg-yellow-500' };
    return { text: 'Keep Trying!', color: 'bg-red-500' };
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
              <h1 className="text-4xl font-bold text-gray-800 mb-2">Quiz Complete!</h1>
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
                You scored {result.score} out of {result.total_questions} questions correctly
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
                🏠 Back to Home
              </button>
              <button
                onClick={() => startQuiz(quiz)}
                className="bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
              >
                🔄 Retake Quiz
              </button>
              <button
                onClick={() => setShowMistakes(!showMistakes)}
                className="bg-orange-600 text-white py-3 rounded-lg hover:bg-orange-700 transition duration-200 font-semibold"
              >
                {showMistakes ? '👁️ Hide Review' : '📝 Review Mistakes'}
              </button>
            </div>
          </div>

          {/* Mistakes Review */}
          {showMistakes && detailedResults && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h3 className="text-2xl font-semibold text-gray-800 mb-6">📝 Detailed Review</h3>
              
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
                        {questionResult.is_correct ? '✅ Correct' : '❌ Wrong'}
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
                        <p className="text-sm font-semibold text-gray-600 mb-2">Your Answer:</p>
                        <p className={`p-2 rounded ${
                          questionResult.is_correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {questionResult.user_answer}
                        </p>
                      </div>
                      
                      {!questionResult.is_correct && (
                        <div>
                          <p className="text-sm font-semibold text-gray-600 mb-2">Correct Answer:</p>
                          <p className="p-2 rounded bg-green-100 text-green-800">
                            {questionResult.correct_answer}
                          </p>
                        </div>
                      )}
                    </div>

                    {!questionResult.is_correct && (
                      <div className="mt-3">
                        <p className="text-sm font-semibold text-gray-600 mb-2">All Options:</p>
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
                <h4 className="font-semibold text-blue-800 mb-2">Summary:</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-green-600 font-semibold">Correct: </span>
                    {detailedResults.filter(q => q.is_correct).length} questions
                  </div>
                  <div>
                    <span className="text-red-600 font-semibold">Incorrect: </span>
                    {mistakes.length} questions
                  </div>
                  <div>
                    <span className="text-blue-600 font-semibold">Accuracy: </span>
                    {result.percentage.toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Leaderboard */}
          {leaderboard && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-2xl font-semibold text-gray-800 mb-6">🏆 Quiz Leaderboard</h3>
              
              {/* Top 3 */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-700 mb-4">Top 3 Performers</h4>
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
                        {entry.score}/{entry.total_questions} correct
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* User's Position */}
              {leaderboard.user_position && (
                <div className="mb-6 p-4 bg-indigo-50 rounded-lg">
                  <h4 className="text-lg font-semibold text-indigo-800 mb-2">Your Position</h4>
                  <p className="text-indigo-700">
                    You ranked <span className="font-bold">#{leaderboard.user_position.rank}</span> out of{' '}
                    <span className="font-bold">{leaderboard.total_participants}</span> participants!
                  </p>
                </div>
              )}

              {/* Quiz Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-800">{leaderboard.total_participants}</p>
                  <p className="text-sm text-gray-600">Total Participants</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-800">{leaderboard.quiz_stats.total_attempts}</p>
                  <p className="text-sm text-gray-600">Total Attempts</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-800">{leaderboard.quiz_stats.average_score.toFixed(1)}%</p>
                  <p className="text-sm text-gray-600">Average Score</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;