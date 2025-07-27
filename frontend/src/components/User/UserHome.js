import React, { useState } from 'react';

const UserHome = ({ quizzes, startQuiz }) => {
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
              All Subjects
            </CategoryButton>
            <span className="text-gray-500">→</span>
            <CategoryButton onClick={handleBackToSubcategories} icon="📚">
              {selectedSubject}
            </CategoryButton>
            <span className="text-gray-500">→</span>
            <span className="text-lg font-semibold text-gray-800">📂 {selectedSubcategory}</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-800">
            {selectedSubject} - {selectedSubcategory} Quizzes
          </h2>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {subcategoryQuizzes.map((quiz) => (
            <div key={quiz.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200">
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
              All Subjects
            </CategoryButton>
            <span className="text-gray-500">→</span>
            <span className="text-lg font-semibold text-gray-800">📚 {selectedSubject}</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-800">
            {selectedSubject} Subcategories
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
                  <p className="text-gray-500 mb-4">{quizCount} quiz{quizCount !== 1 ? 'es' : ''}</p>
                  <CategoryButton 
                    onClick={() => setSelectedSubcategory(subcategory)}
                    icon="📖"
                  >
                    View Quizzes
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
      <h2 className="text-3xl font-bold text-gray-800 mb-6">📚 Quiz Subjects</h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {subjects.map((subject) => {
          const subcategoryCount = Object.keys(groupedQuizzes[subject]).length;
          const totalQuizCount = Object.values(groupedQuizzes[subject])
            .reduce((total, quizzes) => total + quizzes.length, 0);

          return (
            <div
              key={subject}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200"
            >
              <div className="text-center">
                <div className="text-5xl mb-4">{getSubjectIcon(subject)}</div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">{subject}</h3>
                <p className="text-gray-500 mb-2">{subcategoryCount} subcategor{subcategoryCount !== 1 ? 'ies' : 'y'}</p>
                <p className="text-gray-500 mb-4">{totalQuizCount} quiz{totalQuizCount !== 1 ? 'es' : ''}</p>
                <CategoryButton 
                  onClick={() => setSelectedSubject(subject)}
                  icon="🗂️"
                >
                  Explore {subject}
                </CategoryButton>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default UserHome;