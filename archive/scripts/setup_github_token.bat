@echo off
REM GitHub Token 設定腳本
REM 使用方式：先取得 GitHub Token，然後執行此腳本

echo ===================================================
echo 設定 GitHub Personal Access Token (PAT)
echo ===================================================
echo.
echo 第一步：取得 GitHub Token
echo 1. 前往 https://github.com/settings/tokens
echo 2. 點擊 "Generate new token" (classic)
echo 3. 勾選權限：repo (完整存取權)
echo 4. 產生 token 並複製（只會顯示一次！）
echo.
echo 第二步：輸入 Token
echo.

set /p GITHUB_TOKEN="請貼上您的 GitHub Token: "

echo.
echo 正在設定 Git 憑證...

REM 使用 credential helper 儲存 token
git config --global credential.helper store
echo https://%GITHUB_TOKEN%@github.com > ~/.git-credentials

echo.
echo ✓ Token 已儲存到 Git 憑證
echo.
echo 現在您可以執行 git push，不需要每次輸入密碼
echo.
pause
