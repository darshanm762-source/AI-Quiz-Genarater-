# AI Quiz Generator

## 📌 Overview

**AI Quiz Generator** is a web-based application that automatically generates multiple-choice quizzes on any topic using Artificial Intelligence. Users can enter a topic, choose a difficulty level, and instantly receive a quiz with timed questions. The application evaluates answers, calculates scores, and provides a detailed performance report.

---

# 🚀 Features

* Generate AI-powered quizzes on any topic
* Multiple Choice Questions (MCQs)
* Configurable number of questions
* Difficulty levels:

  * Easy
  * Medium
  * Hard
* 30-second timer for each question
* Automatic navigation when time expires
* Previous/Next question navigation
* Progress bar
* Auto-save answers
* Randomized questions and options
* Instant score calculation
* Detailed result and review page
* User authentication (optional)
* Leaderboard (optional)
* Certificate generation (optional)
* Download results as PDF
* Mobile-friendly responsive design
* Dark and Light mode

---

# 🛠️ Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap 5

## Backend

* Python 3.x
* Flask

## Database

* SQLite

## AI Integration

* OpenAI API or Google Gemini API

---

# 📂 Project Structure

```text
AI-Quiz-Generator/
│
├── app.py
├── config.py
├── models.py
├── routes.py
├── utils.py
├── requirements.txt
├── database.db
│
├── templates/
│   ├── index.html
│   ├── quiz.html
│   ├── result.html
│   └── review.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
```

---

# ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/AI-Quiz-Generator.git
```

### 2. Navigate to the Project Folder

```bash
cd AI-Quiz-Generator
```

### 3. Create a Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the AI API Key

Create a `.env` file and add your API key.

```env
OPENAI_API_KEY=your_api_key_here
```

or

```env
GEMINI_API_KEY=your_api_key_here
```

### 6. Run the Application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

# 📖 How It Works

1. Open the application.
2. Enter a quiz topic.
3. Select the number of questions.
4. Choose the difficulty level.
5. Click **Generate Quiz**.
6. AI generates unique multiple-choice questions.
7. Answer each question before the timer expires.
8. Submit the quiz.
9. View your score and detailed review.

---

# ⏱️ Quiz Timer

* 30 seconds per question
* Countdown displayed on screen
* Automatically moves to the next question when time expires
* Saves unanswered questions

---

# 📊 Result Summary

After submission, the application displays:

* Total Questions
* Correct Answers
* Incorrect Answers
* Unanswered Questions
* Percentage Score
* Grade
* Time Taken

---

# 🗄️ Database Schema

## Quiz

| Field      | Type     |
| ---------- | -------- |
| id         | Integer  |
| topic      | String   |
| difficulty | String   |
| created_at | DateTime |

## Questions

| Field    | Type    |
| -------- | ------- |
| id       | Integer |
| quiz_id  | Integer |
| question | Text    |
| option_a | String  |
| option_b | String  |
| option_c | String  |
| option_d | String  |
| answer   | String  |

## Results

| Field        | Type     |
| ------------ | -------- |
| id           | Integer  |
| quiz_id      | Integer  |
| score        | Integer  |
| percentage   | Float    |
| completed_at | DateTime |

---

# 🔌 API Endpoints

| Method | Endpoint         | Description           |
| ------ | ---------------- | --------------------- |
| POST   | `/generate-quiz` | Generate a new quiz   |
| GET    | `/quiz/<id>`     | Retrieve quiz details |
| POST   | `/submit-quiz`   | Submit quiz answers   |
| GET    | `/results/<id>`  | View quiz results     |

---

# ✨ Future Enhancements

* Voice-based quiz
* AI-generated explanations
* Image-based questions
* Multiplayer quiz mode
* Email result reports
* Question bookmarking
* Analytics dashboard
* Admin panel
* Cloud database support
* Docker deployment

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

# 📄 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

**Your Name**

GitHub: https://github.com/your-username

---

# 🙏 Acknowledgements

* Python
* Flask
* Bootstrap
* OpenAI
* Google Gemini
* SQLite
* JavaScript Community
