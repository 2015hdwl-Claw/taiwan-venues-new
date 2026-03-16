#!/usr/bin/env python3
"""
自動同步系統
功能：Git 自動化、Vercel 自動部署、驗證部署結果
作者：Jobs (Global CTO)
日期：2026-03-17
"""

import subprocess
import json
import time
import requests
from datetime import datetime
import logging
from typing import Dict, List, Optional
import os

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
VERCEL_API_URL = "https://api.vercel.com"
DEPLOY_TIMEOUT = 300  # 秒

class AutoSyncSystem:
    """自動同步系統"""
    
    def __init__(self, vercel_token: str = None, github_token: str = None):
        self.vercel_token = vercel_token or os.getenv('VERCEL_TOKEN')
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.changes = []
    
    def git_status(self) -> Dict:
        """檢查 Git 狀態"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            return {
                'has_changes': len(changed_files) > 0,
                'changed_files': changed_files,
                'count': len(changed_files)
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git 狀態檢查失敗: {e}")
            return {'has_changes': False, 'changed_files': [], 'count': 0}
    
    def generate_commit_message(self, changes: List[Dict]) -> str:
        """生成 commit message"""
        if not changes:
            return "chore: 自動資料更新"
        
        # 統計變更類型
        venue_updates = sum(1 for c in changes if c.get('type') == 'venue_update')
        photo_updates = sum(1 for c in changes if c.get('type') == 'photo_update')
        corrections = sum(1 for c in changes if c.get('type') == 'correction')
        
        parts = []
        if venue_updates > 0:
            parts.append(f"更新 {venue_updates} 個場地資料")
        if photo_updates > 0:
            parts.append(f"更新 {photo_updates} 張照片")
        if corrections > 0:
            parts.append(f"修正 {corrections} 處錯誤")
        
        if parts:
            return f"chore: {', '.join(parts)}"
        else:
            return "chore: 自動資料更新"
    
    def git_add(self, files: List[str] = None):
        """Git add"""
        try:
            if files:
                cmd = ['git', 'add'] + files
            else:
                cmd = ['git', 'add', '.']
            
            subprocess.run(cmd, check=True)
            logger.info(f"Git add 完成")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git add 失敗: {e}")
            return False
    
    def git_commit(self, message: str):
        """Git commit"""
        try:
            subprocess.run(
                ['git', 'commit', '-m', message],
                check=True
            )
            logger.info(f"Git commit 完成: {message}")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit 失敗: {e}")
            return False
    
    def git_push(self, branch: str = 'main'):
        """Git push"""
        try:
            subprocess.run(
                ['git', 'push', 'origin', branch],
                check=True
            )
            logger.info(f"Git push 完成: {branch}")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git push 失敗: {e}")
            return False
    
    def trigger_vercel_deploy(self) -> Optional[str]:
        """觸發 Vercel 部署"""
        if not self.vercel_token:
            logger.warning("未設定 VERCEL_TOKEN，跳過 Vercel 部署")
            return None
        
        try:
            # 使用 Vercel API 觸發部署
            headers = {
                'Authorization': f'Bearer {self.vercel_token}',
                'Content-Type': 'application/json'
            }
            
            # 這裡需要替換為實際的 project ID
            project_id = os.getenv('VERCEL_PROJECT_ID')
            
            response = requests.post(
                f"{VERCEL_API_URL}/v13/deployments",
                headers=headers,
                json={
                    'name': 'taiwan-venues-new',
                    'projectId': project_id,
                    'target': 'production'
                }
            )
            
            if response.status_code == 200:
                deployment = response.json()
                deployment_id = deployment.get('id')
                logger.info(f"Vercel 部署已觸發: {deployment_id}")
                return deployment_id
            else:
                logger.error(f"Vercel 部署觸發失敗: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Vercel 部署觸發異常: {e}")
            return None
    
    def wait_for_deployment(self, deployment_id: str, timeout: int = DEPLOY_TIMEOUT) -> bool:
        """等待部署完成"""
        if not self.vercel_token:
            return True
        
        logger.info(f"等待部署完成 (最多 {timeout} 秒)...")
        
        headers = {
            'Authorization': f'Bearer {self.vercel_token}'
        }
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"{VERCEL_API_URL}/v13/deployments/{deployment_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    deployment = response.json()
                    status = deployment.get('status')
                    
                    if status == 'ready':
                        logger.info("部署成功！")
                        return True
                    elif status in ['error', 'canceled']:
                        logger.error(f"部署失敗: {status}")
                        return False
                    
                    logger.info(f"部署狀態: {status}")
                
                time.sleep(5)
            
            except Exception as e:
                logger.error(f"檢查部署狀態失敗: {e}")
                time.sleep(5)
        
        logger.error("部署超時")
        return False
    
    def verify_deployment(self, url: str = 'https://taiwan-venues-new.vercel.app') -> bool:
        """驗證部署結果"""
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"部署驗證成功: {url}")
                return True
            else:
                logger.error(f"部署驗證失敗: HTTP {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"部署驗證異常: {e}")
            return False
    
    def sync_to_production(self, changes: List[Dict] = None) -> bool:
        """同步到生產環境"""
        logger.info("開始同步到生產環境")
        
        # 1. 檢查是否有變更
        status = self.git_status()
        if not status['has_changes']:
            logger.info("沒有變更需要同步")
            return True
        
        # 2. Git add
        if not self.git_add():
            return False
        
        # 3. 生成 commit message
        commit_msg = self.generate_commit_message(changes or [])
        
        # 4. Git commit
        if not self.git_commit(commit_msg):
            return False
        
        # 5. Git push
        if not self.git_push():
            return False
        
        # 6. 觸發 Vercel 部署
        deployment_id = self.trigger_vercel_deploy()
        
        # 7. 等待部署完成
        if deployment_id:
            if not self.wait_for_deployment(deployment_id):
                self.rollback()
                return False
        
        # 8. 驗證部署結果
        if not self.verify_deployment():
            logger.error("部署驗證失敗")
            return False
        
        logger.info("同步完成！")
        return True
    
    def rollback(self):
        """回滾變更"""
        logger.warning("執行回滾...")
        
        try:
            # Git reset
            subprocess.run(['git', 'reset', '--hard', 'HEAD~1'], check=True)
            
            # 強制 push
            subprocess.run(['git', 'push', '-f', 'origin', 'main'], check=True)
            
            logger.info("回滾完成")
        
        except subprocess.CalledProcessError as e:
            logger.error(f"回滾失敗: {e}")
    
    def log_sync(self, changes: List[Dict], success: bool):
        """記錄同步"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'changes': changes,
            'success': success
        }
        
        self.changes.append(log_entry)
        
        # 儲存到日誌檔案
        with open('logs/sync_history.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自動同步系統')
    parser.add_argument('--sync', action='store_true', help='執行同步')
    parser.add_argument('--status', action='store_true', help='檢查狀態')
    parser.add_argument('--verify', action='store_true', help='驗證部署')
    
    args = parser.parse_args()
    
    # 建立必要目錄
    os.makedirs('logs', exist_ok=True)
    
    system = AutoSyncSystem()
    
    if args.status:
        status = system.git_status()
        print(f"變更檔案數: {status['count']}")
        if status['changed_files']:
            print("變更檔案:")
            for file in status['changed_files']:
                print(f"  {file}")
    
    elif args.verify:
        success = system.verify_deployment()
        print(f"部署驗證: {'成功' if success else '失敗'}")
    
    elif args.sync:
        success = system.sync_to_production()
        print(f"同步結果: {'成功' if success else '失敗'}")
    
    else:
        print("請指定要執行的操作")


if __name__ == '__main__':
    main()
