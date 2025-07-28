import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../App';
import { FaThumbsUp, FaComment, FaTag, FaUser, FaShieldAlt, FaClock } from 'react-icons/fa';
import axios from 'axios';

const Home = () => {
  const { user, API } = useAuth();
  const [searchParams] = useSearchParams();
  const [questions, setQuestions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchQuestions();
    fetchCategories();
  }, [selectedCategory, searchParams]);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedCategory) params.category = selectedCategory;
      
      const response = await axios.get(`${API}/questions`, { params });
      setQuestions(response.data);
    } catch (error) {
      setError('Failed to fetch questions');
      console.error('Error fetching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleLike = async (questionId) => {
    if (!user) {
      alert('Please login to like questions');
      return;
    }

    try {
      await axios.post(`${API}/questions/${questionId}/like`);
      fetchQuestions(); // Refresh questions to update like count
    } catch (error) {
      console.error('Error liking question:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-1/4">
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-6">
            <h2 className="text-lg font-semibold mb-4">Categories</h2>
            <div className="space-y-2">
              <button
                onClick={() => setSelectedCategory('')}
                className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                  selectedCategory === '' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'hover:bg-gray-100'
                }`}
              >
                All Questions
              </button>
              {categories.map((category) => (
                <button
                  key={category.name}
                  onClick={() => setSelectedCategory(category.name)}
                  className={`w-full text-left px-3 py-2 rounded-md transition-colors flex items-center justify-between ${
                    selectedCategory === category.name 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <span>{category.name}</span>
                  <span className="text-sm text-gray-500">({category.question_count})</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:w-3/4">
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-900">
                  {selectedCategory ? `Questions in ${selectedCategory}` : 'All Questions'}
                </h1>
                {user && (
                  <Link
                    to="/create-question"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Ask Question
                  </Link>
                )}
              </div>
            </div>

            <div className="divide-y">
              {questions.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <p>No questions found.</p>
                  {user && (
                    <Link
                      to="/create-question"
                      className="text-blue-600 hover:text-blue-800 mt-2 inline-block"
                    >
                      Be the first to ask a question!
                    </Link>
                  )}
                </div>
              ) : (
                questions.map((question) => (
                  <div key={question.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <FaTag className="w-4 h-4 text-blue-600" />
                          <span className="text-sm text-blue-600 font-medium">
                            {question.category}
                          </span>
                        </div>
                        
                        <Link
                          to={`/question/${question.id}`}
                          className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition-colors"
                        >
                          {question.title}
                        </Link>
                        
                        <p className="text-gray-600 mt-2 line-clamp-2">
                          {question.content}
                        </p>
                        
                        <div className="flex items-center justify-between mt-4">
                          <div className="flex items-center space-x-4">
                            <button
                              onClick={() => handleLike(question.id)}
                              className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
                                question.is_liked 
                                  ? 'bg-blue-100 text-blue-700' 
                                  : 'hover:bg-gray-100'
                              }`}
                            >
                              <FaThumbsUp className="w-4 h-4" />
                              <span>{question.likes_count}</span>
                            </button>
                            
                            <div className="flex items-center space-x-1 text-gray-500">
                              <FaComment className="w-4 h-4" />
                              <span>{question.answers_count}</span>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2 text-sm text-gray-500">
                            <FaUser className="w-4 h-4" />
                            <Link
                              to={`/profile/${question.author_id}`}
                              className="hover:text-blue-600 transition-colors flex items-center space-x-1"
                            >
                              <span>{question.author_name}</span>
                              {question.author_is_admin && (
                                <FaShield className="w-3 h-3 text-yellow-500" title="Admin" />
                              )}
                            </Link>
                            <span>•</span>
                            <div className="flex items-center space-x-1">
                              <FaClock className="w-4 h-4" />
                              <span>{formatDate(question.created_at)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;