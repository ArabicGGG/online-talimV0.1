# Online Learning Platform - Replit.md

## Overview

This is a Flask-based online learning platform that allows instructors to create and manage courses while students can enroll and access learning materials. The platform features course management, user authentication, video lessons, and a shopping cart system for course purchases.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (configured via environment variable, can be switched to PostgreSQL)
- **Authentication**: Flask-Login for session management
- **File Upload**: Werkzeug for handling video and image uploads
- **Security**: Password hashing with Werkzeug security utilities

### Frontend Architecture
- **Template Engine**: Jinja2 templates
- **CSS Framework**: Tailwind CSS via CDN
- **Icons**: Font Awesome 6.0
- **JavaScript**: Vanilla JS with class-based architecture
- **Responsive Design**: Mobile-first approach with Tailwind utilities

### Database Schema
- **Users**: Authentication, roles (student/instructor)
- **Courses**: Course information, pricing, categories
- **Lessons**: Video content, ordering, course association
- **Enrollments**: Student-course relationships with progress tracking
- **Comments & Ratings**: User feedback system

## Key Components

### Authentication System
- Role-based access control (student/instructor)
- Session-based authentication using Flask-Login
- Password hashing for security
- Registration with email validation

### Course Management
- Instructors can create courses with video lessons
- File upload system for videos (MP4, AVI, MOV, etc.)
- Course categorization and pricing
- Featured courses system

### Shopping Cart
- Session-based cart storage
- Course purchase workflow
- Price calculation and display

### Video Streaming
- HTML5 video player with multiple format support
- File serving through Flask static routes
- Lesson progression tracking

### User Dashboard
- Role-specific interfaces
- Course statistics for instructors
- Enrollment tracking for students

## Data Flow

1. **User Registration/Login**: User creates account → Flask-Login manages sessions
2. **Course Creation**: Instructor uploads course content → Files stored in uploads/ directory
3. **Course Discovery**: Students browse courses → Cart system manages selections
4. **Enrollment**: Students enroll in courses → Progress tracking begins
5. **Learning**: Students access lessons → Video streaming and progress updates

## External Dependencies

### Python Packages
- Flask (web framework)
- SQLAlchemy (ORM)
- Flask-Login (authentication)
- Werkzeug (utilities and security)

### Frontend Dependencies
- Tailwind CSS (styling)
- Font Awesome (icons)
- Vanilla JavaScript (interactions)

### File Storage
- Local file system for uploads
- Configured upload directory with size limits (500MB)

## Deployment Strategy

### Development Setup
- SQLite database for local development
- Flask development server on port 5000
- Debug mode enabled
- Environment variables for configuration

### Production Considerations
- DATABASE_URL environment variable for PostgreSQL
- SESSION_SECRET for secure sessions
- ProxyFix middleware for reverse proxy deployment
- File upload security with allowed extensions

### File Structure
```
/
├── app.py (main application)
├── main.py (entry point)
├── models.py (database models)
├── templates/ (Jinja2 templates)
├── static/ (CSS, JS, images)
└── uploads/ (user uploaded files)
```

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 04, 2025. Initial setup