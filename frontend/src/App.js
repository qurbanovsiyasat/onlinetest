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

  const deleteQuiz = async (quizId) => {
    if (window.confirm('Are you sure you want to delete this quiz?')) {
      try {
        await apiCall(`/admin/quiz/${quizId}`, { method: 'DELETE' });
        fetchQuizzes();
      } catch (error) {
        alert('Error deleting quiz');
      }
    }
  };

  const editQuiz = (quiz) => {
    setEditingQuiz(quiz);
    setShowEditModal(true);
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
    } catch (error) {
      alert('Error updating quiz visibility');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">All Quizzes (Sorted by Date)</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {quizzes.map((quiz) => (
          <div key={quiz.id} className="border rounded-lg p-4 relative">
            <div className="mb-2">
              <span className={`inline-block px-2 py-1 rounded text-xs ${
                quiz.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {quiz.is_public ? 'Public' : 'Private'}
              </span>
              <span className="inline-block px-2 py-1 rounded text-xs bg-blue-100 text-blue-800 ml-1">
                {quiz.subject_folder}
              </span>
            </div>
            
            <h3 className="font-semibold text-gray-800 mb-2">{quiz.title}</h3>
            <p className="text-gray-600 text-sm mb-2">{quiz.description}</p>
            
            <div className="flex justify-between items-center text-sm text-gray-500 mb-3">
              <span>{quiz.category}</span>
              <span>{quiz.total_questions} questions</span>
            </div>
            
            <div className="text-xs text-gray-400 mb-3">
              Created: {new Date(quiz.created_at).toLocaleDateString()}
              {quiz.updated_at !== quiz.created_at && (
                <div>Updated: {new Date(quiz.updated_at).toLocaleDateString()}</div>
              )}
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => editQuiz(quiz)}
                className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition duration-200 text-sm"
              >
                ✏️ Edit
              </button>
              <button
                onClick={() => toggleQuizVisibility(quiz)}
                className={`flex-1 py-2 rounded transition duration-200 text-sm ${
                  quiz.is_public 
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700' 
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {quiz.is_public ? '🔒 Make Private' : '🔓 Make Public'}
              </button>
              <button
                onClick={() => deleteQuiz(quiz.id)}
                className="flex-1 bg-red-600 text-white py-2 rounded hover:bg-red-700 transition duration-200 text-sm"
              >
                🗑️ Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Edit Quiz Modal */}
      {showEditModal && editingQuiz && (
        <QuizEditModal
          quiz={editingQuiz}
          onClose={() => setShowEditModal(false)}
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
    subject_folder: quiz.subject_folder,
    is_public: quiz.is_public,
    is_active: quiz.is_active
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate(quiz.id, editData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h3 className="text-lg font-semibold mb-4">Edit Quiz: {quiz.title}</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
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
            <label className="block text-gray-700 font-semibold mb-2">Description</label>
            <textarea
              value={editData.description}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
              rows="3"
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

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Subject Folder</label>
            <select
              value={editData.subject_folder}
              onChange={(e) => setEditData({ ...editData, subject_folder: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
            >
              <option value="General">General</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Science">Science</option>
              <option value="History">History</option>
              <option value="Language">Language</option>
              <option value="Geography">Geography</option>
              <option value="Art">Art</option>
              <option value="Technology">Technology</option>
            </select>
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={editData.is_public}
                onChange={(e) => setEditData({ ...editData, is_public: e.target.checked })}
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

          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition duration-200"
            >
              Update Quiz
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition duration-200"
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

  return (
    <div className="bg-white rounded-lg shadow p-6">
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
  );
}

function AdminCreateQuiz({ setCurrentView }) {
  const [quiz, setQuiz] = useState({
    title: '',
    description: '',
    category: '',
    subject_folder: 'General',
    is_public: false,
    allowed_users: [],
    questions: []
  });

  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: '',
    options: [
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ],
    image_url: null
  });

  const [uploadingImage, setUploadingImage] = useState(false);
  const [allUsers, setAllUsers] = useState([]);
  const [showUserSelection, setShowUserSelection] = useState(false);

  useEffect(() => {
    if (quiz.is_public) {
      fetchAllUsers();
    }
  }, [quiz.is_public]);

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

    const imageUrl = await uploadImage(file);
    if (imageUrl) {
      setCurrentQuestion({ ...currentQuestion, image_url: imageUrl });
    }
  };

  const removeImage = () => {
    setCurrentQuestion({ ...currentQuestion, image_url: null });
  };

  const addQuestion = () => {
    if (!currentQuestion.question_text || !currentQuestion.options.every(opt => opt.text) || !currentQuestion.options.some(opt => opt.is_correct)) {
      alert('Please fill all fields and select correct answer');
      return;
    }

    setQuiz({
      ...quiz,
      questions: [...quiz.questions, { ...currentQuestion, id: Date.now().toString() }]
    });
    
    setCurrentQuestion({
      question_text: '',
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ],
      image_url: null
    });
  };

  const createQuiz = async () => {
    if (!quiz.title || !quiz.description || !quiz.category || quiz.questions.length === 0) {
      alert('Please fill all fields and add at least one question');
      return;
    }

    if (quiz.is_public && quiz.allowed_users.length === 0) {
      alert('Please select at least one user for public quiz access');
      return;
    }

    try {
      await apiCall('/admin/quiz', {
        method: 'POST',
        data: quiz
      });
      alert('Quiz created successfully!');
      setCurrentView('quizzes');
    } catch (error) {
      alert('Error creating quiz: ' + (error.response?.data?.detail || 'Unknown error'));
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

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Create New Quiz</h2>
      
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-gray-700 font-semibold mb-2">Quiz Title</label>
          <input
            type="text"
            value={quiz.title}
            onChange={(e) => setQuiz({ ...quiz, title: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg"
            placeholder="Enter quiz title"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-semibold mb-2">Description</label>
          <textarea
            value={quiz.description}
            onChange={(e) => setQuiz({ ...quiz, description: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg"
            rows="3"
            placeholder="Describe your quiz"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Category</label>
            <input
              type="text"
              value={quiz.category}
              onChange={(e) => setQuiz({ ...quiz, category: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
              placeholder="Enter category (e.g., Math, Science)"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">Subject Folder</label>
            <select
              value={quiz.subject_folder}
              onChange={(e) => setQuiz({ ...quiz, subject_folder: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg"
            >
              <option value="General">General</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Science">Science</option>
              <option value="History">History</option>
              <option value="Language">Language</option>
              <option value="Geography">Geography</option>
              <option value="Art">Art</option>
              <option value="Technology">Technology</option>
            </select>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex items-center mb-4">
            <input
              type="checkbox"
              id="isPublic"
              checked={quiz.is_public}
              onChange={(e) => setQuiz({ ...quiz, is_public: e.target.checked, allowed_users: [] })}
              className="mr-3"
            />
            <label htmlFor="isPublic" className="font-semibold text-gray-700">
              Make this quiz public (accessible to selected users)
            </label>
          </div>

          {quiz.is_public && (
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Select Users Who Can Access This Quiz ({quiz.allowed_users.length} selected)
              </label>
              <div className="max-h-40 overflow-y-auto border border-gray-300 rounded-lg p-3">
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

      {/* Add Question Form */}
      <div className="bg-gray-50 p-6 rounded-lg mb-6">
        <h3 className="text-lg font-semibold mb-4">Add Question</h3>
        
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">Question</label>
          <input
            type="text"
            value={currentQuestion.question_text}
            onChange={(e) => setCurrentQuestion({ ...currentQuestion, question_text: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg"
            placeholder="Enter your question"
          />
        </div>

        {/* Image Upload Section */}
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">Question Image (Optional)</label>
          {!currentQuestion.image_url ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="imageUpload"
                disabled={uploadingImage}
              />
              <label
                htmlFor="imageUpload"
                className={`cursor-pointer inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200 ${
                  uploadingImage ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {uploadingImage ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    📷 Upload Image
                  </>
                )}
              </label>
              <p className="text-sm text-gray-500 mt-2">
                Supported formats: JPG, PNG, GIF, WEBP (max 5MB)
              </p>
            </div>
          ) : (
            <div className="relative">
              <img
                src={currentQuestion.image_url}
                alt="Question"
                className="max-w-full h-auto rounded-lg shadow"
                style={{ maxHeight: '300px' }}
              />
              <button
                onClick={removeImage}
                className="absolute top-2 right-2 bg-red-600 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-700 transition duration-200"
              >
                ✕
              </button>
            </div>
          )}
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">Options</label>
          {currentQuestion.options.map((option, index) => (
            <div key={index} className="flex items-center mb-2">
              <input
                type="radio"
                name="correct-answer"
                checked={option.is_correct}
                onChange={() => {
                  const updatedOptions = currentQuestion.options.map((opt, i) => ({
                    ...opt,
                    is_correct: i === index
                  }));
                  setCurrentQuestion({ ...currentQuestion, options: updatedOptions });
                }}
                className="mr-3"
              />
              <input
                type="text"
                value={option.text}
                onChange={(e) => {
                  const updatedOptions = [...currentQuestion.options];
                  updatedOptions[index].text = e.target.value;
                  setCurrentQuestion({ ...currentQuestion, options: updatedOptions });
                }}
                className="flex-1 p-2 border border-gray-300 rounded-lg"
                placeholder={`Option ${String.fromCharCode(65 + index)}`}
              />
            </div>
          ))}
        </div>

        <button
          onClick={addQuestion}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
        >
          Add Question
        </button>
      </div>

      {/* Questions Preview */}
      {quiz.questions.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Questions Added ({quiz.questions.length})</h3>
          <div className="space-y-4">
            {quiz.questions.map((question, index) => (
              <div key={index} className="bg-blue-50 p-4 rounded-lg">
                <p className="font-semibold mb-2">{index + 1}. {question.question_text}</p>
                {question.image_url && (
                  <div className="mb-3">
                    <img
                      src={question.image_url}
                      alt="Question"
                      className="max-w-full h-auto rounded-lg shadow"
                      style={{ maxHeight: '200px' }}
                    />
                  </div>
                )}
                <div className="grid grid-cols-2 gap-2">
                  {question.options.map((option, optIndex) => (
                    <div key={optIndex} className={`p-2 rounded ${option.is_correct ? 'bg-green-100 text-green-800' : 'bg-gray-100'}`}>
                      {String.fromCharCode(65 + optIndex)}. {option.text}
                      {option.is_correct && ' ✓'}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-4">
        <button
          onClick={createQuiz}
          className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
        >
          Create Quiz
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
      alert('Error submitting quiz');
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
                    <div className="mb-2">
                      <span className="inline-block bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                        {quiz.category}
                      </span>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">{quiz.title}</h3>
                    <p className="text-gray-600 mb-4">{quiz.description}</p>
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-sm text-gray-500">{quiz.total_questions} questions</span>
                      <span className="text-sm text-gray-500">
                        {new Date(quiz.created_at).toLocaleDateString()}
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
    </div>
  );
}

// User Quiz Taking Components
function UserTakeQuiz({ quiz, currentQuestionIndex, setCurrentQuestionIndex, userAnswers, selectAnswer, nextQuestion, setCurrentView }) {
  if (!quiz) return null;

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;

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
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            {currentQuestion.question_text}
          </h2>

          {currentQuestion.image_url && (
            <div className="mb-6">
              <img
                src={currentQuestion.image_url}
                alt="Question"
                className="max-w-full h-auto rounded-lg shadow"
              />
            </div>
          )}

          <div className="space-y-4 mb-8">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => selectAnswer(option.text)}
                className={`w-full p-4 text-left rounded-lg border-2 transition duration-200 ${
                  userAnswers[currentQuestionIndex] === option.text
                    ? 'border-teal-500 bg-teal-50 text-teal-800'
                    : 'border-gray-200 hover:border-teal-300 hover:bg-teal-50'
                }`}
              >
                <span className="font-semibold mr-3">{String.fromCharCode(65 + index)}.</span>
                {option.text}
              </button>
            ))}
          </div>

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
              disabled={!userAnswers[currentQuestionIndex]}
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
  if (!result) return null;

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">🎉 Quiz Complete!</h1>
            <h2 className="text-2xl font-semibold text-gray-700 mb-6">{quiz.title}</h2>
          </div>

          <div className="mb-8">
            <div className="text-6xl font-bold mb-4">
              <span className={getScoreColor(result.percentage)}>
                {result.percentage.toFixed(1)}%
              </span>
            </div>
            <p className="text-xl text-gray-600 mb-2">
              You scored {result.score} out of {result.total_questions} questions correctly
            </p>
            <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
              <div
                className={`h-4 rounded-full transition-all duration-1000 ${
                  result.percentage >= 80 ? 'bg-green-500' :
                  result.percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${result.percentage}%` }}
              ></div>
            </div>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => setCurrentView('home')}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold"
            >
              🏠 Back to Home
            </button>
            <button
              onClick={() => startQuiz(quiz)}
              className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
            >
              🔄 Retake Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;