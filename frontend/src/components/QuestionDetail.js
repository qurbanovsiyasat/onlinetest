import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../App';
import { 
  FaThumbsUp, FaComment, FaTag, FaUser, FaShield, FaClock, FaReply 
} from 'react-icons/fa';
import axios from 'axios';

const QuestionDetail = () => {
  const { questionId } = useParams();
  const { user, API } = useAuth();
  const [question, setQuestion] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [newAnswer, setNewAnswer] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchQuestion();
    fetchAnswers();
  }, [questionId]);

  const fetchQuestion = async () => {
    try {
      const response = await axios.get(`${API}/questions/${questionId}`);
      setQuestion(response.data);
    } catch (error) {
      setError('Question not found');
      console.error('Error fetching question:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnswers = async () => {
    try {
      const response = await axios.get(`${API}/questions/${questionId}/answers`);
      setAnswers(response.data);
    } catch (error) {
      console.error('Error fetching answers:', error);
    }
  };

  const handleLikeQuestion = async () => {
    if (!user) {
      alert('Please login to like questions');
      return;
    }

    try {
      await axios.post(`${API}/questions/${questionId}/like`);
      fetchQuestion(); // Refresh question to update like count
    } catch (error) {
      console.error('Error liking question:', error);
    }
  };

  const handleLikeAnswer = async (answerId) => {
    if (!user) {
      alert('Please login to like answers');
      return;
    }

    try {
      await axios.post(`${API}/answers/${answerId}/like`);
      fetchAnswers(); // Refresh answers to update like count
    } catch (error) {
      console.error('Error liking answer:', error);
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();
    if (!user) {
      alert('Please login to submit answers');
      return;
    }

    if (!newAnswer.trim()) {
      alert('Please enter your answer');
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API}/questions/${questionId}/answers`, {
        content: newAnswer
      });
      setNewAnswer('');
      fetchAnswers(); // Refresh answers
      fetchQuestion(); // Refresh question to update answer count
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setSubmitting(false);
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

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <h3 className="text-lg font-medium text-red-800 mb-2">
            {error}
          </h3>
          <Link to="/" className="text-blue-600 hover:text-blue-800">
            Back to Questions
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Question */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <FaTag className="w-4 h-4 text-blue-600" />
          <span className="text-sm text-blue-600 font-medium bg-blue-50 px-2 py-1 rounded">
            {question.category}
          </span>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {question.title}
        </h1>
        
        <div className="prose max-w-none mb-6">
          <p className="text-gray-700 text-lg leading-relaxed">
            {question.content}
          </p>
        </div>
        
        <div className="flex items-center justify-between border-t pt-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleLikeQuestion}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                question.is_liked 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'hover:bg-gray-100'
              }`}
            >
              <FaThumbsUp className="w-4 h-4" />
              <span>{question.likes_count}</span>
            </button>
            
            <div className="flex items-center space-x-2 text-gray-500">
              <FaComment className="w-4 h-4" />
              <span>{question.answers_count} answers</span>
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

      {/* Answer Form */}
      {user && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <FaReply className="w-5 h-5 mr-2 text-blue-600" />
            Your Answer
          </h3>
          <form onSubmit={handleSubmitAnswer}>
            <textarea
              value={newAnswer}
              onChange={(e) => setNewAnswer(e.target.value)}
              placeholder="Write your answer here..."
              className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="6"
              required
            />
            <div className="flex justify-end mt-4">
              <button
                type="submit"
                disabled={submitting}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Submitting...' : 'Submit Answer'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Answers */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b">
          <h3 className="text-xl font-semibold">
            {answers.length} {answers.length === 1 ? 'Answer' : 'Answers'}
          </h3>
        </div>
        
        {answers.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <FaComment className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No answers yet. Be the first to answer!</p>
          </div>
        ) : (
          <div className="divide-y">
            {answers.map((answer) => (
              <div key={answer.id} className="p-6">
                <div className="prose max-w-none mb-4">
                  <p className="text-gray-700 leading-relaxed">
                    {answer.content}
                  </p>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => handleLikeAnswer(answer.id)}
                      className={`flex items-center space-x-2 px-3 py-1 rounded-lg transition-colors ${
                        answer.is_liked 
                          ? 'bg-blue-100 text-blue-700' 
                          : 'hover:bg-gray-100'
                      }`}
                    >
                      <FaThumbsUp className="w-4 h-4" />
                      <span>{answer.likes_count}</span>
                    </button>
                  </div>
                  
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <FaUser className="w-4 h-4" />
                    <Link
                      to={`/profile/${answer.author_id}`}
                      className="hover:text-blue-600 transition-colors flex items-center space-x-1"
                    >
                      <span>{answer.author_name}</span>
                      {answer.author_is_admin && (
                        <FaShield className="w-3 h-3 text-yellow-500" title="Admin" />
                      )}
                    </Link>
                    <span>•</span>
                    <div className="flex items-center space-x-1">
                      <FaClock className="w-4 h-4" />
                      <span>{formatDate(answer.created_at)}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionDetail;