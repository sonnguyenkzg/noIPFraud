#!/usr/bin/env python3
"""
noIPFraud API Client
Base implementation for n8n automation
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any


class NoIPFraudAPI:
    """API client for noIPFraud platform"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.token_expiry = None
    
    def login(self) -> bool:
        """
        Authenticate and get token
        Token valid for 5 hours per API docs
        """
        url = f"{self.base_url}/login.php"
        payload = {
            "username": self.username,
            "password": self.password
        }
        params = {"a": "auth"}
        
        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get("token")
            self.token_expiry = datetime.now() + timedelta(hours=5)
            
            print(f"✅ Login successful")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def _ensure_authenticated(self):
        """Check token validity and re-login if needed"""
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            print("🔄 Token expired, re-authenticating...")
            self.login()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
    
    # ==================== CAMPAIGN OPERATIONS ====================
    
    def get_campaigns(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """
        Get list of campaigns
        
        Args:
            from_date: Start date (YYYY-MM-DD), defaults to today
            to_date: End date (YYYY-MM-DD), defaults to today
        
        Returns:
            List of campaign objects
        """
        self._ensure_authenticated()
        
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            to_date = from_date
        
        url = f"{self.base_url}/campaigns.php"
        params = {
            "a": "list",
            "from": from_date,
            "to": to_date
        }
        
        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Get campaigns failed: {e}")
            return []
    
    def change_status(self, campaign_id: str, status: int) -> bool:
        """
        Change campaign status
        
        Args:
            campaign_id: Campaign ID (e.g., 'xmgbl4i3')
            status: Status code
                0 = Under Review
                1 = Active
                2 = Allow All
                -1 = Block All
        
        Returns:
            True if successful
        """
        self._ensure_authenticated()
        
        url = f"{self.base_url}/campaigns.php"
        params = {
            "a": "changeStatus",
            "clid": campaign_id,
            "status": status
        }
        
        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            print(f"✅ Changed {campaign_id} to status {status}")
            return True
        except Exception as e:
            print(f"❌ Change status failed: {e}")
            return False
    
    def bulk_change_status(self, campaign_ids: List[str], status: int) -> Dict[str, bool]:
        """
        Change status for multiple campaigns
        
        Args:
            campaign_ids: List of campaign IDs
            status: Target status code
        
        Returns:
            Dict mapping campaign_id to success boolean
        """
        results = {}
        for cid in campaign_ids:
            results[cid] = self.change_status(cid, status)
        return results
    
    def get_campaign_stats(self, campaign_id: str, from_date: str, to_date: str) -> Optional[Dict]:
        """
        Get statistics for a campaign
        
        Args:
            campaign_id: Campaign ID
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
        
        Returns:
            Stats object or None
        """
        self._ensure_authenticated()
        
        url = f"{self.base_url}/stats.php"
        params = {
            "a": "daily",
            "clid": campaign_id,
            "from": from_date,
            "to": to_date
        }
        
        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Get stats failed: {e}")
            return None
    
    # ==================== BULK OPERATIONS ====================
    
    def get_all_campaign_statuses(self) -> List[Dict]:
        """
        Get status for all campaigns
        Returns list of {campaign_id, campaign_name, status, ...}
        """
        campaigns = self.get_campaigns()
        return [
            {
                "campaign_id": c["name"],
                "campaign_name": c["info"],
                "status": c["active"],
                "fakeurl": c.get("fakeurl"),
                "traffic": c.get("traffic")
            }
            for c in campaigns
        ]
    
    def get_block_check_report(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get block rate report for all campaigns
        
        Args:
            date: Date to check (YYYY-MM-DD), defaults to yesterday
        
        Returns:
            List of campaign stats with block rates
        """
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        campaigns = self.get_campaigns(date, date)
        report = []
        
        for campaign in campaigns:
            total = campaign.get("total", 0)
            blocked = campaign.get("block", 0)
            block_rate = (blocked / total * 100) if total > 0 else 0
            
            report.append({
                "campaign_id": campaign["name"],
                "campaign_name": campaign["info"],
                "date": date,
                "total_clicks": total,
                "blocked_clicks": blocked,
                "allowed_clicks": total - blocked,
                "block_rate": round(block_rate, 2),
                "flag": "🚨 HIGH" if block_rate > 50 else "✅ OK"
            })
        
        return report


# ==================== USAGE EXAMPLES ====================

def main():
    # Initialize client
    api = NoIPFraudAPI(
        base_url="https://luxeattic.com/admin/api",
        username="luxeattic",
        password="Z456789xAa"
    )
    
    # Login
    if not api.login():
        return
    
    print("\n" + "="*70)
    print("TEST 1: Get All Campaigns")
    print("="*70)
    campaigns = api.get_campaigns()
    print(f"Found {len(campaigns)} campaigns")
    if campaigns:
        print(f"First: {campaigns[0]['info']}")
    
    print("\n" + "="*70)
    print("TEST 2: Get Campaign Statuses")
    print("="*70)
    statuses = api.get_all_campaign_statuses()
    for s in statuses[:3]:
        print(f"{s['campaign_name']}: status={s['status']}")
    
    print("\n" + "="*70)
    print("TEST 3: Change Single Campaign Status")
    print("="*70)
    if campaigns:
        test_campaign = campaigns[0]["name"]
        api.change_status(test_campaign, 1)  # Set to Active
    
    print("\n" + "="*70)
    print("TEST 4: Bulk Change Status")
    print("="*70)
    if len(campaigns) >= 3:
        campaign_ids = [c["name"] for c in campaigns[:3]]
        results = api.bulk_change_status(campaign_ids, 1)
        print(f"Changed {sum(results.values())}/{len(results)} campaigns")
    
    print("\n" + "="*70)
    print("TEST 5: Block Check Report")
    print("="*70)
    report = api.get_block_check_report()
    print(f"\nBlock Rate Report ({len(report)} campaigns):")
    for r in report[:5]:
        print(f"{r['campaign_name']}: {r['total_clicks']} clicks, "
              f"{r['block_rate']}% blocked {r['flag']}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()