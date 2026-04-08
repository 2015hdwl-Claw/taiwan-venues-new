#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 GitHub 倉儲權限並提供解決方案
"""

import subprocess
import sys
import io

# 設定 UTF-8 輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_command(cmd):
    """執行命令並返回結果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def main():
    print("=" * 60)
    print("GitHub 推送權限檢查與設定")
    print("=" * 60)
    print()

    # 1. 檢查當前 git 配置
    print("📋 步驟 1: 檢查 Git 配置")
    print("-" * 60)

    username, _ = run_command("git config user.name")
    email, _ = run_command("git config user.email")
    remote_url, _ = run_command("git remote get-url origin")

    print(f"Git 使用者: {username}")
    print(f"Email: {email}")
    print(f"遠端倉儲: {remote_url}")
    print()

    # 2. 分析倉儲所屬
    print("🔍 步驟 2: 分析倉儲權限")
    print("-" * 60)

    if "2015hdwl-Claw" in remote_url:
        print("❌ 問題：倉儲屬於 2015hdwl-Claw")
        print(f"   但您的 Git 配置為: {username}")
        print()

        # 3. 提供解決方案
        print("💡 解決方案")
        print("-" * 60)
        print()
        print("方案 A: 使用正確的 GitHub 帳號")
        print("   1. 如果您是 2015hdwl-Claw，請更新 Git 配置：")
        print("      git config user.name \"2015hdwl-Claw\"")
        print()
        print("方案 B: 將自己加入為協作者")
        print("   1. 聯絡倉儲擁有者將您加入為 collaborator")
        print("   2. 或前往: https://github.com/2015hdwl-Claw/taiwan-venues-new/settings/access")
        print()
        print("方案 C: 使用 Personal Access Token")
        print("   1. 前往: https://github.com/settings/tokens")
        print("   2. 產生新 token (勾選 repo 權限)")
        print("   3. 執行: setup_github_token.bat")
        print()

    # 4. 測試推送
    print("🚀 步驟 3: 測試推送")
    print("-" * 60)
    print("正在測試推送...")
    print()

    output, code = run_command("git push origin main --dry-run")

    if code == 0:
        print("✅ 推送測試成功！可以執行 git push")
    else:
        print(f"❌ 推送測試失敗 (錯誤代碼: {code})")
        print(f"   {output}")
        print()
        print("請按照上述解決方案修正權限問題")

    print()
    print("=" * 60)

if __name__ == '__main__':
    main()
