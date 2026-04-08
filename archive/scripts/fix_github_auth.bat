@echo off
echo ===================================================
echo 清除舊的 Git 憑證並重新認證
echo ===================================================
echo.
echo 正在清除舊憑證...
cmdkey /delete:git:https://github.com 2>nul
echo ✓ 舊憑證已清除
echo.
echo ===================================================
echo 現在請執行以下步驟：
echo ===================================================
echo.
echo 1. 手動執行 git push：
echo    cd c:\Users\ntpud\.claude\projects\taiwan-venues-new\taiwan-venues-new
echo    git push origin main
echo.
echo 2. 輸入您的 GitHub 帳號資訊：
echo    - 使用者名稱: 2015hdwl-Claw
echo    - 密碼: 您的 GitHub 密碼或 Personal Access Token
echo.
echo 注意：如果使用兩步驟驗證，必須使用 Personal Access Token
echo.
pause
