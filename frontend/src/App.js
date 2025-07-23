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

  useEffect(() => {
    if (currentView === 'users') fetchUsers();
    if (currentView === 'quizzes') fetchQuizzes();
    if (currentView === 'categories') fetchCategories();
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
        {currentView === 'dashboard' && <AdminDashboardHome />}
        {currentView === 'users' && <AdminUsersView users={users} />}
        {currentView === 'quizzes' && <AdminQuizzesView quizzes={quizzes} fetchQuizzes={fetchQuizzes} />}
        {currentView === 'categories' && <AdminCategoriesView categories={categories} fetchCategories={fetchCategories} />}
        {currentView === 'create-quiz' && <AdminCreateQuiz setCurrentView={setCurrentView} />}
      </div>
    </div>
  );
}

// Admin Dashboard Components
function AdminDashboardHome() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">📊 Overview</h3>
        <p className="text-gray-600">Manage your quiz platform from here</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">👥 Users</h3>
        <p className="text-gray-600">View and manage registered users</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">📝 Quizzes</h3>
        <p className="text-gray-600">Create and manage quizzes</p>
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

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">All Quizzes</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {quizzes.map((quiz) => (
          <div key={quiz.id} className="border rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">{quiz.title}</h3>
            <p className="text-gray-600 text-sm mb-2">{quiz.description}</p>
            <div className="flex justify-between items-center text-sm text-gray-500 mb-3">
              <span>{quiz.category}</span>
              <span>{quiz.total_questions} questions</span>
            </div>
            <button
              onClick={() => deleteQuiz(quiz.id)}
              className="w-full bg-red-600 text-white py-2 rounded hover:bg-red-700 transition duration-200"
            >
              Delete Quiz
            </button>
          </div>
        ))}
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
    questions: []
  });

  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: '',
    options: [
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ]
  });

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
      ]
    });
  };

  const createQuiz = async () => {
    if (!quiz.title || !quiz.description || !quiz.category || quiz.questions.length === 0) {
      alert('Please fill all fields and add at least one question');
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
      alert('Error creating quiz');
    }
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
            placeholder="Enter quiz description"
          />
        </div>

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