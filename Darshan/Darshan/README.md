# AI Quiz Generator Web Application

A feature-rich, full-stack AI Quiz Generator built with **Python (Flask)**, **SQLite (SQLAlchemy)**, **Bootstrap 5**, and **JavaScript**.

---

## Features

- 🤖 **AI-Powered Question Generation**: Accepts any topic, question count (5–50, default 20), and difficulty level (*Easy*, *Medium*, *Hard*). Supports **Gemini API** and **OpenAI API**, with an intelligent fallback engine when offline or unconfigured.
- ⏱️ **Per-Question Countdown Timer**: 30-second timer per question with visual warnings, sound effects, and auto-advance when time expires.
- 📊 **Instant Grading & Analysis**: Automatic percentage score calculation, academic letter grades (A, B, C, D, F), detailed breakdown of correct, wrong, and unanswered questions.
- 💡 **Answer Review Mode**: Comprehensive step-by-step breakdown of each question displaying user answer, correct answer, and AI explanation.
- 📜 **Printable Accomplishment Certificate**: Generates official PDF-printable accomplishment certificates with unique verification codes.
- 🔊 **Web Audio API Synthesizer**: Native sound effects for timer warnings, option clicks, and victory chimes without external MP3 file dependencies.
- 💾 **Local Storage State Persistence**: Saves selected answers locally so interrupted or refreshed quizzes can be seamlessly resumed.
- 🏆 **Global Leaderboard & Admin Dashboard**: Monitor top scores across quizzes, view user results, delete test sessions, and export full reports as CSV.
- 🌓 **Dark / Light Mode**: Seamless UI theme toggling.

---

## Folder Structure

```
project/
│
├── app.py                  # Flask application setup & runner
├── config.py               # Application settings & secret keys
├── models.py               # SQLAlchemy database models (User, Quiz, Question, Result)
├── routes.py               # View routes, REST API endpoints, Auth & Admin handlers
├── utils.py                # AI Integration (Gemini/OpenAI) + Fallback Generator
├── schema.sql              # Relational SQL Database Schema
├── database.db             # SQLite database (auto-generated)
├── requirements.txt        # Python package dependencies
├── README.md               # Setup & usage documentation
│
├── templates/
│   ├── base.html           # Master layout with Navbar, Theme Switcher, Footer
│   ├── index.html          # Quiz setup dashboard & topic launcher
│   ├── quiz.html           # Interactive quiz taking interface with timer
│   ├── result.html         # Quiz score analysis & grade display
│   ├── review.html         # Question-by-question review with AI explanations
│   ├── certificate.html    # Printable accomplishment certificate
│   ├── leaderboard.html    # Global top scores & rankings
│   ├── login.html          # User authentication sign-in
│   ├── signup.html         # User registration page
│   └── admin.html          # Admin dashboard & CSV export center
│
└── static/
    ├── css/
    │   └── style.css       # Custom modern CSS styling, glassmorphism, gradients
    └── js/
        ├── main.js         # AJAX request handling & global utilities
        ├── quiz.js         # Interactive quiz controller, 30s timer & localstorage state
        ├── sound.js        # Web Audio API sound synthesizer
        └── theme.js        # Dark/Light theme toggler
```

---

## Installation & Setup Guide

### 1. Prerequisites
- Python 3.8+ installed on your machine.

### 2. Install Dependencies
In your terminal, navigate to the project directory and install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional)
Create a `.env` file in the root directory if you wish to connect your OpenAI or Gemini API key:

```env
SECRET_KEY=ai-quiz-generator-secret-key-2026
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

*(If no API keys are provided, the app automatically switches to the built-in Intelligent Fallback Quiz Engine so you can test immediately without any configuration!)*

### 4. Launch Application
Run the Flask server:

```bash
python app.py
```

Open your browser and navigate to:
`http://127.0.0.1:5000`

---

## REST API Endpoints

### 1. Generate Quiz
- **Endpoint**: `POST /generate-quiz` or `POST /api/generate-quiz`
- **Request Body (JSON)**:
  ```json
  {
    "topic": "Python Programming",
    "difficulty": "Medium",
    "num_questions": 20
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "quiz_id": 1,
    "redirect_url": "/quiz/1",
    "message": "Quiz generated successfully!"
  }
  ```

### 2. Fetch Quiz Details
- **Endpoint**: `GET /quiz/<id>/data` or `GET /api/quiz/<id>`
- **Response**: Returns quiz metadata and array of questions.

### 3. Submit Quiz Answers
- **Endpoint**: `POST /submit-quiz` or `POST /api/submit-quiz`
- **Request Body (JSON)**:
  ```json
  {
    "quiz_id": 1,
    "answers": {
      "1": "Python",
      "2": "Option B"
    }
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "result_id": 1,
    "score": 16,
    "total_questions": 20,
    "percentage": 80.0,
    "grade": "A",
    "redirect_url": "/result/1"
  }
  ```

### 4. Fetch Quiz Result
- **Endpoint**: `GET /results/<id>` or `GET /api/results/<id>`

### 5. Admin CSV Export
- **Endpoint**: `GET /admin/export-csv`
- **Response**: Downloads `quiz_results_export.csv`.

---

## License
Built for educational and demonstration purposes.
