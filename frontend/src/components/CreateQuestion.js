import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { FaTag, FaQuestion, FaEdit } from 'react-icons/fa';
import axios from 'axios';

const CreateQuestion = () => {
  const { user, API } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: ''
  });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if not logged in
  if (!user) {
    navigate('/login');
    return null;
  }

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!formData.title.trim() || !formData.content.trim() || !formData.category) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${API}/questions`, formData);
      navigate(`/question/${response.data.id}`);
    } catch (error) {
      setError('Failed to create question. Please try again.');
      console.error('Error creating question:', error);
    } finally {
      setLoading(false);
    }
  };

  const predefinedCategories = [
    'Mathematics', 'Science', 'History', 'Literature', 'Technology', 
    'Health', 'Sports', 'Art', 'Music', 'Philosophy', 'Psychology', 
    'Economics', 'Politics', 'Education', 'Travel', 'Food', 'Other'
  ];

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FaQuestion className="w-6 h-6 mr-3 text-blue-600" />
            Ask a Question
          </h1>
          <p className="text-gray-600 mt-2">
            Share your question with the community and get helpful answers.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Question Title
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="What would you like to ask?"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Be specific and clear about what you're asking.
            </p>
          </div>

          {/* Category */}
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
              <FaTag className="inline w-4 h-4 mr-1" />
              Category
            </label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Select a category</option>
              {predefinedCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
            <p className="text-sm text-gray-500 mt-1">
              Choose the most relevant category for your question.
            </p>
          </div>

          {/* Content */}
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
              <FaEdit className="inline w-4 h-4 mr-1" />
              Question Details
            </label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleChange}
              placeholder="Provide more details about your question..."
              rows="8"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Include any relevant context, examples, or what you've already tried.
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-sm text-red-600">{error}</div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Publishing...
                </div>
              ) : (
                'Publish Question'
              )}
            </button>
          </div>
        </form>

        {/* Guidelines */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-sm font-medium text-blue-800 mb-2">
            Tips for asking great questions:
          </h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Be specific and clear about what you're asking</li>
            <li>• Include relevant context and background information</li>
            <li>• Choose the most appropriate category</li>
            <li>• Check if your question has already been asked</li>
            <li>• Be respectful and constructive in your language</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CreateQuestion;