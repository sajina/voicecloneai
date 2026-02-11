# Railway Deployment Guide

Follow these steps to deploy **VoiceCloneAI** to [Railway.com](https://railway.app/).

## Prerequisites
- A Railway account.
- This repository pushed to your GitHub.

---

## Step 1: Create Project & Database
1. Go to your **Railway Dashboard**.
2. Click **New Project** -> **Empty Project**.
3. In the new project, click **+ New** -> **Database** -> **MySQL**.
   - This will create a MySQL service.
   - Click on the MySQL service card -> **Variables** tab.
   - Copy the following variables (you'll need them later):
     - `MYSQL_URL` (Full connection string)
     - `MYSQLHOST`
     - `MYSQLPORT`
     - `MYSQLUSER`
     - `MYSQLPASSWORD`
     - `MYSQLDATABASE`

---

## Step 2: Deploy Backend (Django)
1. In the same project, click **+ New** -> **GitHub Repo**.
2. Select your repository: `sajina/voicecloneai`.
3. Select **Add Variables** immediately (before deploying).
4. Add the following **Environment Variables** for the backend service:

   | Variable | Value / Description |
   |----------|---------------------|
   | `ENVIRONMENT` | `production` |
   | `SECRET_KEY` | (Generate a strong random string) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `*` (or your specific domain) |
   | `CORS_ALLOWED_ORIGINS` | `https://your-frontend-domain.up.railway.app,http://localhost:5173` |
   | `CSRF_TRUSTED_ORIGINS` | `https://your-backend-domain.up.railway.app,https://your-frontend-domain.up.railway.app` |
   | `DATABASE_URL` | Check MySQL Variables (or use `${{MySQL.MYSQL_URL}}` if Railway supports linking) |
   | `MYSQL_URL` | `${{MySQL.MYSQL_URL}}` (Use Reference Variable feature) |
   | `EMAIL_HOST` | `smtp.gmail.com` |
   | `EMAIL_PORT` | `587` |
   | `EMAIL_USE_TLS` | `True` |
   | `EMAIL_HOST_USER` | Your Gmail address |
   | `EMAIL_HOST_PASSWORD` | Your Gmail App Password |

5. **Settings** -> **General** -> **Root Directory**: Set to `/backend` (Important!).

6. **Settings** -> **Networking** -> **Generate Domain**.
   - This will give you a backend URL like `voicecloneai-production.up.railway.app`.
   - **Update** `CSRF_TRUSTED_ORIGINS` with this URL.

7. **Deploy**.

---

## Step 3: Deploy Frontend (React + Vite)
1. Click **+ New** -> **GitHub Repo** (select the same repo again).
2. Go to **Settings** -> **General** -> **Root Directory**: Set to `/frontend` (Important!).
3. Go to **Variables** and add:

   | Variable | Value |
   |----------|-------|
   | `VITE_API_URL` | Your Backend URL (e.g., `https://voicecloneai-production.up.railway.app`) (No trailing slash) |

4. **Settings** -> **Networking** -> **Generate Domain**.
   - This is your frontend URL (e.g., `voicecloneai-frontend.up.railway.app`).

5. **Update Backend Variables:**
   - Go back to your Backend service variables.
   - Update `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to include your new **Frontend URL**.
   - Redeploy Backend.

---

## Step 4: Run Migrations & Create Superuser
1. Click on the **Backend Service** card.
2. Go to the **Command** tab (or check specific Railway CLI instructions).
   - *Note: Our `entrypoint.sh` automatically runs migrations on start.*
   - If migrations fail, check logs.
3. Open **Railway CLI** or **Shell** (if available in dashboard) to create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Troubleshooting
- **Build Failed?** Check the Build Logs. Ensure paths in Dockerfile are relative to the root context.
- **CORS Errors?** Ensure `CORS_ALLOWED_ORIGINS` in backend matches the frontend URL exactly (no trailing slash).
- **CSRF Errors?** Ensure `CSRF_TRUSTED_ORIGINS` includes `https://` + backend AND frontend domains.
