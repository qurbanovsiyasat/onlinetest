import React, { useState, useEffect } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useAuth } from '../App';
import { 
  FaUser, FaShield, FaUserPlus, FaUserMinus, FaLock, 
  FaClock, FaThumbsUp, FaComment, FaTag, FaEnvelope
} from 'react-icons/fa';
import axios from 'axios';

const Profile = () => {
  const { userId } = useParams();
  const { user, API } = useAuth();
  const [profileUser, setProfileUser] = useState(null);
  const [userQuestions, setUserQuestions] = useState([]);
  const [userAnswers, setUserAnswers] = useState([]);
  const [activeTab, setActiveTab] = useState('questions');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isFollowing, setIsFollowing] = useState(false);

  useEffect(() => {
    fetchProfile();
    fetchUserQuestions();
    fetchUserAnswers();
  }, [userId]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API}/users/${userId}`);
      setProfileUser(response.data);
      
      // Check if current user is following this profile
      if (user && user.id !== userId) {
        checkFollowStatus();
      }
    } catch (error) {
      if (error.response?.status === 403) {
        setError('This profile is private');
      } else {
        setError('User not found');
      }
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserQuestions = async () => {
    try {
      const response = await axios.get(`${API}/users/${userId}/questions`);
      setUserQuestions(response.data);
    } catch (error) {
      console.error('Error fetching user questions:', error);
    }
  };

  const fetchUserAnswers = async () => {
    try {
      const response = await axios.get(`${API}/users/${userId}/answers`);
      setUserAnswers(response.data);
    } catch (error) {
      console.error('Error fetching user answers:', error);
    }
  };

  const checkFollowStatus = async () => {
    // This would need to be implemented in the backend
    // For now, we'll assume not following
    setIsFollowing(false);
  };

  const handleFollow = async () => {
    if (!user) {
      alert('Please login to follow users');
      return;
    }

    try {
      await axios.post(`${API}/users/${userId}/follow`);
      setIsFollowing(!isFollowing);
      // Refresh profile to update follower count
      fetchProfile();
    } catch (error) {
      console.error('Error following user:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
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
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <FaLock className="mx-auto h-12 w-12 text-yellow-600 mb-4" />
          <h3 className="text-lg font-medium text-yellow-800 mb-2">
            {error}
          </h3>
          <p className="text-yellow-700">
            {error === 'This profile is private' 
              ? 'This user has chosen to keep their profile private.'
              : 'The user you are looking for could not be found.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Profile Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
          <div className="flex items-center space-x-4 mb-4 sm:mb-0">
            <div className="h-20 w-20 bg-blue-100 rounded-full flex items-center justify-center">
              <FaUser className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-bold text-gray-900">{profileUser.full_name}</h1>
                {profileUser.is_admin && (
                  <FaShield className="h-5 w-5 text-yellow-500" title="Admin" />
                )}
              </div>
              <p className="text-gray-600">@{profileUser.username}</p>
              <div className="flex items-center space-x-1 text-sm text-gray-500">
                <FaEnvelope className="h-4 w-4" />
                <span>{profileUser.email}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <div className="text-xl font-bold text-gray-900">{profileUser.followers_count}</div>
              <div className="text-sm text-gray-500">Followers</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-gray-900">{profileUser.following_count}</div>
              <div className="text-sm text-gray-500">Following</div>
            </div>
            
            {user && user.id !== userId && (
              <button
                onClick={handleFollow}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  isFollowing
                    ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isFollowing ? (
                  <>
                    <FaUserMinus className="h-4 w-4" />
                    <span>Unfollow</span>
                  </>
                ) : (
                  <>
                    <FaUserPlus className="h-4 w-4" />
                    <span>Follow</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
        
        <div className="mt-4 flex items-center space-x-2 text-sm text-gray-500">
          <FaClock className="h-4 w-4" />
          <span>Joined {formatDate(profileUser.created_at)}</span>
        </div>
      </div>

      {/* Profile Tabs */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('questions')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'questions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Questions ({userQuestions.length})
            </button>
            <button
              onClick={() => setActiveTab('answers')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'answers'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Answers ({userAnswers.length})
            </button>
            <button
              onClick={() => setActiveTab('activity')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'activity'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Activity
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'questions' && (
            <div className="space-y-4">
              {userQuestions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No questions yet.</p>
              ) : (
                userQuestions.map((question) => (
                  <div key={question.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <FaTag className="h-4 w-4 text-blue-600" />
                          <span className="text-sm text-blue-600 font-medium">
                            {question.category}
                          </span>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                          {question.title}
                        </h3>
                        <p className="text-gray-600 mb-3">{question.content}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <div className="flex items-center space-x-1">
                            <FaThumbsUp className="h-4 w-4" />
                            <span>{question.likes_count}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <FaComment className="h-4 w-4" />
                            <span>{question.answers_count}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <FaClock className="h-4 w-4" />
                            <span>{formatDate(question.created_at)}</span>
                          </div>
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
                <p className="text-gray-500 text-center py-8">No answers yet.</p>
              ) : (
                userAnswers.map((answer) => (
                  <div key={answer.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-gray-900 mb-3">{answer.content}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <div className="flex items-center space-x-1">
                            <FaThumbsUp className="h-4 w-4" />
                            <span>{answer.likes_count}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <FaClock className="h-4 w-4" />
                            <span>{formatDate(answer.created_at)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'activity' && (
            <div className="text-center py-8">
              <p className="text-gray-500">Activity timeline coming soon!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;