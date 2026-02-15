# AI Voice Cloning Application

A professional-grade text-to-speech application with voice cloning, translation, and admin capabilities.

## 🚀 Features

- **140+ Neural Voices** across 55 languages
- **Voice Cloning** capabilities
- **Multi-language Translation** (55+ languages)
- **User Management** & Admin Dashboard
- **Credit System** for usage tracking

## 🛠 Tech Stack

- **Frontend:** React, Vite, TailwindCSS
- **Backend:** Django, Django REST Framework
- **Database:** MySQL / PostgreSQL (Railway)
- **TTS Engine:** Microsoft Edge TTS

---

## ☁️ Deployment on Railway

This project is optimized for [Railway](https://railway.app/).

### 1. Deploy the Repo
1. Fork this repository.
2. Login to Railway and creating a "New Project" -> "Deploy from GitHub".
3. Select this repo. Railway will automatically detect the `Dockerfile` for backend and frontend.

### 2. Configure Networking & Environment
You need to generate public domains for both services:
1. Go to **Settings -> Networking** for each service.
2. Click **"Generate Domain"**.
3. Copy these domains for step 3.

### 3. Environment Variables

#### Backend Service Variables
| Variable | Value | Description |
|---|---|---|
| `ALLOWED_HOSTS` | `*` | Or your backend domain |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend.up.railway.app` | Frontend URL |
| `CSRF_TRUSTED_ORIGINS` | `https://your-backend.up.railway.app` | Backend URL |
| `FRONTEND_URL` | `https://your-frontend.up.railway.app` | Used for CORS auto-config |
| `SECRET_KEY` | `(generate random string)` | Security key |
| `DATABASE_URL` | (Auto-set by Railway if you add a DB) | Connection string |
| `ENVIRONMENT` | `production` | Enables prod settings |

#### Frontend Service Variables
| Variable | Value | Description |
|---|---|---|
| `VITE_API_URL` | `https://your-backend.up.railway.app` | Backend URL |

> **Important:** After updating `VITE_API_URL`, you must **Redeploy** the Frontend service.

### 4. Persistence (Recommended)
To keep generated audio files and voice clones across redeploys:
1. Go to Backend Service -> **Volumes**.
2. Click **"Add Volume"**.
3. Mount path: `/app/media`.

### 5. Database (Optional but Recommended)
Railway puts ephemeral data in a container. For persistence:
1. Add a **PostgreSQL** or **MySQL** service in Railway.
2. It will automatically link `DATABASE_URL` to your backend.

### 6. Email Configuration (Gmail SMTP - Free)
If you don't have a custom domain for Resend, use Gmail:

1.  **Generate App Password**: Go to Google Account -> Security -> App Passwords.
2.  **Railway Variables**:
    *   **DELETE** `RESEND_API_KEY` (Important!).
    *   Set `EMAIL_HOST_USER` = `your@gmail.com`
    *   Set `EMAIL_HOST_PASSWORD` = `16-digit-app-password`
    *   Set `DEFAULT_FROM_EMAIL` = `your@gmail.com`

---

## 🔐 Admin Access

The application automatically creates a superuser on first deploy:

- **Email:** `admin@example.com`
- **Password:** `admin123`

Login at `/admin` (Backend) or via the Frontend Login page.
**Change this password immediately after logging in!**

---

## 💻 Local Development

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
