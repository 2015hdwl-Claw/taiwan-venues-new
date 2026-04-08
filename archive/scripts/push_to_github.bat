@echo off
echo ===================================================
echo 推送到 GitHub
echo ===================================================
echo.
cd /d "c:\Users\ntpud\.claude\projects\taiwan-venues-new\taiwan-venues-new"
echo 倉儲: 2015hdwl-Claw/taiwan-venues-new
echo 帳號: 2015hdwl-Claw
echo.
echo 正在推送...
echo.

git push origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✓ 推送成功！Vercel 將自動部署
) else (
    echo ❌ 推送失敗
    echo.
    echo 如果提示輸入帳號密碼：
    echo   使用者名稱: 2015hdwl-Claw
    echo   密碼: 您的 GitHub 密碼或 Personal Access Token
    echo.
    echo 如果是 403 錯誤，可能需要：
    echo   1. 清除 Windows 憑證管理器中的舊憑證
    echo   2. 或使用 Personal Access Token
)

echo.
pause
