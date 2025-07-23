import { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [quizzes, setQuizzes] = useState([]);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [quizResult, setQuizResult] = useState(null);

  // Quiz creation state
  const [newQuiz, setNewQuiz] = useState({
    title: '',
    description: '',
    questions: []
  });

  const [newQuestion, setNewQuestion] = useState({
    question_text: '',
    options: [
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ]
  });

  // Quiz taking state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const fetchQuizzes = async () => {
    try {
      const response = await axios.get(`${API}/quiz`);
      setQuizzes(response.data);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    }
  };

  const addQuestion = () => {
    if (newQuestion.question_text && newQuestion.options.every(opt => opt.text) && newQuestion.options.some(opt => opt.is_correct)) {
      setNewQuiz({
        ...newQuiz,
        questions: [...newQuiz.questions, { ...newQuestion, id: Date.now().toString() }]
      });
      setNewQuestion({
        question_text: '',
        options: [
          { text: '', is_correct: false },
          { text: '', is_correct: false },
          { text: '', is_correct: false },
          { text: '', is_correct: false }
        ]
      });
    } else {
      alert('Please fill all fields and select correct answer');
    }
  };

  const createQuiz = async () => {
    if (newQuiz.title && newQuiz.description && newQuiz.questions.length > 0) {
      try {
        await axios.post(`${API}/quiz`, newQuiz);
        alert('Quiz created successfully!');
        setNewQuiz({ title: '', description: '', questions: [] });
        setCurrentView('home');
        fetchQuizzes();
      } catch (error) {
        console.error('Error creating quiz:', error);
        alert('Error creating quiz');
      }
    } else {
      alert('Please fill all fields and add at least one question');
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
      const response = await axios.post(`${API}/quiz/${selectedQuiz.id}/attempt`, {
        quiz_id: selectedQuiz.id,
        answers: userAnswers
      });
      setQuizResult(response.data);
      setCurrentView('result');
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert('Error submitting quiz');
    }
  };

  const HomeView = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-indigo-900 mb-4">📝 OnlineTestMaker</h1>
          <p className="text-xl text-gray-600 mb-8">Create and take quizzes instantly - no registration required!</p>
          <div className="flex justify-center gap-4">
            <button
              onClick={() => setCurrentView('create')}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition duration-200 font-semibold"
            >
              ➕ Create Quiz
            </button>
          </div>
        </header>

        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Available Quizzes</h2>
          {quizzes.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No quizzes available yet. Be the first to create one!</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {quizzes.map((quiz) => (
                <div key={quiz.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200">
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
      </div>
    </div>
  );

  const CreateQuizView = () => (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <button
            onClick={() => setCurrentView('home')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 font-semibold"
          >
            ← Back to Home
          </button>
          <h1 className="text-4xl font-bold text-purple-900 mb-2">Create New Quiz</h1>
          <p className="text-gray-600">Fill in the details and add questions to create your quiz</p>
        </header>

        <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-lg p-8">
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">Quiz Title</label>
            <input
              type="text"
              value={newQuiz.title}
              onChange={(e) => setNewQuiz({ ...newQuiz, title: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter quiz title..."
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">Quiz Description</label>
            <textarea
              value={newQuiz.description}
              onChange={(e) => setNewQuiz({ ...newQuiz, description: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              rows="3"
              placeholder="Describe your quiz..."
            />
          </div>

          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Add Question</h3>
            <div className="bg-gray-50 p-6 rounded-lg">
              <div className="mb-4">
                <label className="block text-gray-700 font-semibold mb-2">Question Text</label>
                <input
                  type="text"
                  value={newQuestion.question_text}
                  onChange={(e) => setNewQuestion({ ...newQuestion, question_text: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter your question..."
                />
              </div>

              <div className="mb-4">
                <label className="block text-gray-700 font-semibold mb-2">Answer Options</label>
                {newQuestion.options.map((option, index) => (
                  <div key={index} className="flex items-center mb-2">
                    <input
                      type="radio"
                      name="correct-answer"
                      checked={option.is_correct}
                      onChange={() => {
                        const updatedOptions = newQuestion.options.map((opt, i) => ({
                          ...opt,
                          is_correct: i === index
                        }));
                        setNewQuestion({ ...newQuestion, options: updatedOptions });
                      }}
                      className="mr-3"
                    />
                    <input
                      type="text"
                      value={option.text}
                      onChange={(e) => {
                        const updatedOptions = [...newQuestion.options];
                        updatedOptions[index].text = e.target.value;
                        setNewQuestion({ ...newQuestion, options: updatedOptions });
                      }}
                      className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder={`Option ${String.fromCharCode(65 + index)}`}
                    />
                  </div>
                ))}
              </div>

              <button
                onClick={addQuestion}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition duration-200 font-semibold"
              >
                Add Question
              </button>
            </div>
          </div>

          {newQuiz.questions.length > 0 && (
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">Questions Added ({newQuiz.questions.length})</h3>
              <div className="space-y-4">
                {newQuiz.questions.map((question, index) => (
                  <div key={index} className="bg-blue-50 p-4 rounded-lg">
                    <p className="font-semibold text-gray-800 mb-2">{index + 1}. {question.question_text}</p>
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

          <button
            onClick={createQuiz}
            className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold text-lg"
          >
            🚀 Create Quiz
          </button>
        </div>
      </div>
    </div>
  );

  const TakeQuizView = () => {
    if (!selectedQuiz) return null;

    const currentQuestion = selectedQuiz.questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / selectedQuiz.questions.length) * 100;

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
            <h1 className="text-4xl font-bold text-teal-900 mb-2">{selectedQuiz.title}</h1>
            <p className="text-gray-600 mb-4">{selectedQuiz.description}</p>
            
            <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
              <div
                className="bg-teal-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">
              Question {currentQuestionIndex + 1} of {selectedQuiz.questions.length}
            </p>
          </header>

          <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              {currentQuestion.question_text}
            </h2>

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
                {currentQuestionIndex === selectedQuiz.questions.length - 1 ? 'Submit Quiz' : 'Next Question'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const ResultView = () => {
    if (!quizResult) return null;

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
              <h2 className="text-2xl font-semibold text-gray-700 mb-6">{selectedQuiz.title}</h2>
            </div>

            <div className="mb-8">
              <div className="text-6xl font-bold mb-4">
                <span className={getScoreColor(quizResult.percentage)}>
                  {quizResult.percentage.toFixed(1)}%
                </span>
              </div>
              <p className="text-xl text-gray-600 mb-2">
                You scored {quizResult.score} out of {quizResult.total_questions} questions correctly
              </p>
              <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
                <div
                  className={`h-4 rounded-full transition-all duration-1000 ${
                    quizResult.percentage >= 80 ? 'bg-green-500' :
                    quizResult.percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${quizResult.percentage}%` }}
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
                onClick={() => startQuiz(selectedQuiz)}
                className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
              >
                🔄 Retake Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'create':
        return <CreateQuizView />;
      case 'take-quiz':
        return <TakeQuizView />;
      case 'result':
        return <ResultView />;
      default:
        return <HomeView />;
    }
  };

  return (
    <div className="App">
      {renderCurrentView()}
    </div>
  );
}

export default App;