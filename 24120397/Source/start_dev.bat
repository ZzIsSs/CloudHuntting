@echo off
title CloudHunting - Development Server
color 0A

echo =======================================================
echo    Khoi dong CloudHunting voi tinh nang Auto-Reload
echo =======================================================
echo Chu y: Cac service trong start_all.py da duoc cau hinh
echo        uvicorn --reload, nen code se tu dong cap nhat
echo        khi ban chinh sua file trong thu muc src/.
echo =======================================================
echo.

:loop
echo [ %TIME% ] Dang khoi dong he thong...
echo.

REM Kiem tra xem co thu muc venv khong, neu co dung python cua venv
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" start_all.py
) else (
    python start_all.py
)

echo.
echo =======================================================
echo [ %TIME% ] He thong da dung (hoac bi loi).
echo.
echo - Nhan phim bat ky de KHOI DONG LAI toan bo he thong.
echo - Hoac nhan Ctrl+C roi chon Y de thoat hoan toan.
echo =======================================================
pause
goto loop
