@echo off
echo ============================================
echo     MOTOR CHOICE DSS - Khoi dong he thong
echo     AI + AHP + Random Forest + Vue.js 3
echo ============================================
echo.

echo [1/2] Khoi dong Backend (FastAPI)...
start "DSS Backend" cmd /k "cd /d C:\Study\HCMUNRE\HHTRQD\Motor_Choice\backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Khoi dong Frontend (Vue.js + Vite)...
start "DSS Frontend" cmd /k "cd /d C:\Study\HCMUNRE\HHTRQD\Motor_Choice\frontend-vue && npm run dev"

timeout /t 4 /nobreak >nul

echo.
echo ============================================
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo  API Docs: http://localhost:8000/docs
echo ============================================
echo.

start "" http://localhost:5173
