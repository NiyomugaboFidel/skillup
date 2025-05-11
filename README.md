# SkillUp

![SkillUp Logo](https://via.placeholder.com/150x50?text=SkillUp)

> A modular eLearning platform built with Django for accessible, community-driven education

## 📚 Overview

SkillUp is a comprehensive online learning and certification platform designed for simplicity and effectiveness. The platform allows instructors to create concise, modular courses while enabling students to enroll, track progress, and earn certificates upon completion.

## ✨ Core Features

- **User Management**
  - Role-based authentication (Instructor/Student)
  - Personalized dashboards
  - Profile customization

- **Course Creation & Management**
  - Multiple content formats (Video, Notes, PDFs)
  - Lesson organization
  - Resource management

- **Learning Experience**
  - Clean, intuitive interface
  - Progress tracking
  - Quiz assessments with MCQ support
  - PDF certificate generation

- **Enhanced Learning**
  - AI-powered quiz generation and feedback
  - Course recommendations
  - Live sessions via video calls
  - Real-time messaging with instructors and peers

## 🛠️ Tech Stack

### Backend
- Django / Django REST Framework
- Django Channels + Redis
- PostgreSQL / SQLite
- OpenAI Python SDK

### Frontend
- Django Templates / React
- Tailwind CSS

### Media & Communications
- Cloudinary for media storage
- xhtml2pdf / reportlab for certificate generation
- Daily.co / Agora / Jitsi for video integration

## 🏗️ Architecture

```
├── Frontend (Django Templates/React + Tailwind)
├── Backend (Django + Channels)
│   ├── Authentication & Access Control
│   ├── Course Management
│   ├── Enrollment System
│   ├── Progress Tracking
│   ├── Quiz Engine
│   ├── Certificate Generator
│   └── Analytics Dashboard
├── Media Storage (Local/Cloudinary)
├── WebSockets (Redis + Channels)
└── External APIs
    ├── OpenAI Integration
    └── Video Call Services
```

## 📊 Database Models

- **User** (Extended Django User)
- **Course**, **Lesson**, **ContentBlock** (notes, video, pdf)
- **Enrollment**
- **Quiz**, **Question**, **Answer**
- **Progress**
- **Certificate**
- **ChatMessage** (WebSocket)
- **AIQuizLog**

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Redis server
- PostgreSQL (recommended for production)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/NiyomugaboFidel/skillup
   cd skillup
   ```

2. Create and activate virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations
   ```bash
   python manage.py migrate
   ```

6. Start development server
   ```bash
   python manage.py runserver
   ```

## 🌐 Deployment

SkillUp can be deployed on:
- Railway
- Render
- PythonAnywhere
- Any Django-compatible hosting

Important deployment considerations:
- Configure environment variables for API keys
- Set up proper media storage for production
- Ensure Redis server is configured for real-time features
- Secure OpenAI and media APIs with proper authentication

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ for accessible education