# FlyRank Backend AI Internship - BE-03 Auth API

A secure authentication API built using **FastAPI** and **Supabase Auth**.

This project implements user signup, login, logout, JWT token verification, and protected API routes.

The goal is to understand modern backend authentication using an external Identity Provider instead of manually handling passwords and security tokens.

---

# Features

- User Signup
- User Login
- JWT Access Token generation
- Refresh Token support
- Protected API routes
- Bearer Token authentication
- JWT verification using Supabase
- Logout functionality
- Swagger UI authentication testing

---

# Tech Stack

- Python 3.13
- FastAPI
- Supabase Auth
- JWT
- Pydantic
- Uvicorn
- Python-dotenv

---

# Project Structure
BE-03-auth-api/
│ ├── main.py ├── requirements.txt ├── README.md ├── .env ├── .env.example ├── .gitignore │ ├── auth/ │   ├── init.py │   ├── supabase_client.py │   └── dependencies.py │ ├── routes/ │   ├── init.py │   ├── auth_routes.py │   └── protected_routes.py │ └── models/ ├── init.py └── user.py

---

# Architecture
Client | ↓ FastAPI Routes | ↓ Authentication Layer | ↓ Supabase Auth | ↓ JWT Verification | ↓ Protected Resources

---

# Authentication Flow

1. User signs up or logs in through the API.
2. Supabase validates credentials.
3. Supabase returns a JWT Access Token.
4. Client sends the token in the Authorization header.
5. FastAPI verifies the token using Supabase.
6. Valid users can access protected routes.

---

# Environment Setup

Create a `.env` file:
SUPABASE_URL=your_project_url SUPABASE_KEY=your_anon_key

Get these values from:
Supabase Dashboard → Project Settings → API

Never upload `.env` to GitHub.

---

# Installation

Install dependencies:

```bash
pip install -r requirements.txt
Running the Application
Start FastAPI server:
Bash
uvicorn main:app --reload
Application runs at:

http://localhost:8000
Swagger documentation:

http://localhost:8000/docs
API Reference
Method
Endpoint
Authentication
POST
/auth/signup
Public
POST
/auth/login
Public
POST
/auth/logout
JWT Required
GET
/public/info
Public
GET
/protected/profile
JWT Required
GET
/protected/dashboard
JWT Required
API Testing
Signup
POST:

/auth/signup
Body:
JSON
{
    "email": "test@example.com",
    "password": "password123"
}
Login
POST:

/auth/login
Body:
JSON
{
    "email": "test@example.com",
    "password": "password123"
}
Successful response:
JSON
{
    "access_token": "JWT_TOKEN",
    "refresh_token": "REFRESH_TOKEN"
}
Protected Routes
Send JWT token in header:

Authorization: Bearer YOUR_ACCESS_TOKEN
Example:

GET /protected/profile
Valid token:

200 OK
Invalid token:

401 Unauthorized
Swagger UI
FastAPI automatically provides Swagger documentation:

/docs
Protected routes support JWT authentication using the Authorize button.
Add screenshot:

docs/swagger-auth.png
Security
Passwords are managed by Supabase Auth.
JWT tokens are verified before accessing protected routes.
Sensitive credentials are stored in environment variables.
.env is excluded using .gitignore.
Future Improvements
Add role-based authorization
Add user profile database
Add automated tests
Add password reset flow
Add refresh token rotation

This is now ready to paste directly. ✅