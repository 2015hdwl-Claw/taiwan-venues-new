#!/bin/bash
# 🚀 活動大師 B2B 核心文件自動部署

set -e

echo "🎯 活動大師 B2B - 核心文件自動部署"
echo "========================================"

# 進入專案目錄
cd /c/Users/ntpud/.claude/projects/taiwan-venues-new/taiwan-venues-new

# 確認核心文件存在
echo "📋 檢查核心文件..."
core_files=("index.html" "app.js" "style.css" "venues.json" "favicon.svg")
for file in "${core_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失！"
        exit 1
    fi
done

# 清理舊的 Vercel 配置
echo "🧹 清理 Vercel 配置..."
rm -rf .vercel

# 部署到 Vercel
echo "🚀 開始部署..."
echo "正在上傳核心文件到 Vercel..."

vercel --prod --yes

echo ""
echo "✅ 部署完成！"
echo "========================================"
echo "🌐 您的 B2B 平台："
echo "   https://taiwan-venues-new.vercel.app"
echo ""
echo "⏱️  網站可能需要 1-2 分鐘完全生效"
echo "📊 查看 Vercel Dashboard："
echo "   https://vercel.com/dashboard"
echo ""
echo "🎉 企業場地風險管理專家平台已上線！"
