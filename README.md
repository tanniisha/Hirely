# Hirely 

**Hirely** is a full-stack interview preparation platform that leverages Artificial Intelligence to help candidates prepare for technical and HR interviews. The platform combines resume analysis, personalized interview question generation, answer evaluation, and audio transcription to create a realistic and interactive interview experience.


## ✨ Key Features

* **Resume Analysis:** Upload PDF resumes and extract candidate information using PyPDF2.
* **AI Interview Generation:** Generate role-specific interview questions based on skills, experience, and target job roles using Google Gemini.
* **Answer Evaluation:** Analyze candidate responses and provide scores, feedback, strengths, and improvement suggestions.
* **Speech-to-Text Transcription:** Convert audio responses into text using SpeechRecognition and Gemini for voice-based interview practice.
* **Interview Management:** Store interview sessions, questions, answers, and evaluations using Flask-SQLAlchemy.
* **Personalized Interview Experience:** Tailor interview questions and feedback based on the candidate's resume and profile.
* **Modern User Interface:** Built with React and Vite to provide a fast, responsive, and user-friendly experience.


##  Architecture

Hirely follows a **decoupled frontend-backend architecture**, ensuring scalability, maintainability, and seamless AI integration.

### Backend Responsibilities

* REST API development
* AI service integration
* Resume parsing and processing
* Audio transcription handling
* Database management

### Frontend Responsibilities

* Interactive user interface
* Interview workflow management
* Real-time API communication
* Responsive user experience

### Design Principles

* Separation of Concerns
* Modular Service Architecture
* AI-Centric Workflows
* Scalable and Extensible Design

---

## 🛠️ Technology Stack

### Backend

*  Python 3
*  Flask
*  Flask-CORS
*  Flask-SQLAlchemy

### Artificial Intelligence

*  Google Gemini (`google-genai`)

### Audio Processing

*  SpeechRecognition
*  Pydub

### Document Processing

*  PyPDF2

### Frontend

*  React
*  Vite
*  JavaScript

### Development Tools

*  npm
*  ESLint
*  @vitejs/plugin-react
*  python-dotenv

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Node.js 18+
* npm
* Google Gemini API Key

### Clone the Repository

```bash
git clone https://github.com/tanniisha/Hirely
cd Hirely
```

### Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

Run the backend server:

```bash
python run.py
```

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Open:

```text
http://localhost:5173
```

---

## 📂 Project Structure

```text
Hirely
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── __init__.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```  

## 🌟 Highlights

 AI-powered interview preparation

 Personalized resume-based questioning

 Automated answer evaluation and feedback

 Voice-enabled interview practice

 Full-stack web application architecture

 Scalable and modular design

## 🔮 Future Enhancements

*  Video interview support
*  ATS resume scoring and optimization


