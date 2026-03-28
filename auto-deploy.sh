#!/bin/bash
# 🚀 活動大師 B2B 一鍵全自動部署

set -e  # 遇到錯誤立即停止

echo "🎯 活動大師 B2B 平台 - 全自動部署"
echo "================================"

# 進入專案目錄
cd /c/Users/ntpud/.claude/projects/taiwan-venues-new/taiwan-venues-new

# 檢查 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI 未安裝"
    echo "正在安裝 Vercel CLI..."
    npm install -g vercel
    echo "✅ Vercel CLI 安裝完成"
fi

echo "📋 當前代碼狀態："
git status --short

echo "💾 自動提交代碼..."
git add -A
git commit -m "auto: B2B 自動部署 $(date +'%Y-%m-%d %H:%M:%S')" 2>/dev/null || echo "📝 沒有新變更需要提交"

echo "🚀 開始部署到 Vercel..."
echo "這將需要 1-3 分鐘..."

# 使用 Vercel CLI 部署
vercel --prod --yes

echo ""
echo "✅ 部署完成！"
echo "================================"
echo "🌐 訪問您的 B2B 平台："
echo "   https://taiwan-venues-new.vercel.app"
echo ""
echo "📊 查看 Vercel Dashboard："
echo "   https://vercel.com/dashboard"
echo ""
echo "🎉 恭喜！您的企業場地風險管理專家平台已上線！"
