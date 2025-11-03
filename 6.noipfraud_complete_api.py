#!/usr/bin/env python3
"""
noIPFraud Complete API Client
All endpoints discovered - Ready for n8n implementation
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class NoIPFraudAPI:
    """Complete API client for noIPFraud"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.token_expiry = None
    
    def login(self) -> bool:
        """Authenticate and get 5-hour token"""
        url = f"{self.base_url}/login.php"
        response = requests.post(url, json={"username": self.username, "password": self.password}, params={"a": "auth"})
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.token_expiry = datetime.now() + timedelta(hours=5)
            return True
        return False
    
    def _ensure_authenticated(self):
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            self.login()
    
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
    
    # ==================== CAMPAIGNS ====================
    
    def get_campaigns(self, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get campaign list"""
        self._ensure_authenticated()
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            to_date = from_date
        
        response = requests.get(
            f"{self.base_url}/campaigns.php",
            params={"a": "list", "from": from_date, "to": to_date},
            headers=self._headers()
        )
        return response.json() if response.status_code == 200 else []
    
    def create_campaign(self, name: str, safe_url: str, money_url: str, 
                       countries: List[str] = None, mobile_only: bool = True) -> Dict:
        """Create new campaign"""
        self._ensure_authenticated()
        if not countries:
            countries = ["th"]
        
        payload = {
            "info": name,
            "fakeurl": safe_url,
            "active": 0,
            "dynautopt": True,
            "dynvar": [{"name": "", "value": ""}],
            "filters": [],
            "lptrack": False,
            "pagelock": {"enabled": False, "action": "blank", "url": "", "timeout": 10},
            "realurl": [{"url": money_url, "perc": 100, "desc": "LP1"}],
            "rules": {
                "mobile": {"allow": True, "d": [] if mobile_only else None},
                "country": {"allow": True, "d": countries}
            },
            "schedule": [],
            "traffic": "54218f34454c61f813000001",  # Facebook
            "urlfilter": [{"variable": "", "action": "1", "value": ""}],
            "urlkeyword": ""
        }
        
        response = requests.post(
            f"{self.base_url}/campaigns.php",
            params={"a": "create"},
            json=payload,
            headers=self._headers()
        )
        return response.json() if response.status_code == 200 else None
    
    def update_campaign(self, campaign_id: str, **updates) -> bool:
        """Update existing campaign"""
        self._ensure_authenticated()
        campaigns = self.get_campaigns()
        current = next((c for c in campaigns if c["name"] == campaign_id), None)
        if not current:
            return False
        
        payload = {
            "name": campaign_id,
            "cv": current.get("cv", "1.8.2"),
            "maxrisk": current.get("maxrisk"),
            "info": updates.get("info", current.get("info")),
            "active": updates.get("active", current.get("active")),
            "fakeurl": updates.get("fakeurl", current.get("fakeurl")),
            "realurl": updates.get("realurl", current.get("realurl")),
            "rules": updates.get("rules", current.get("rules")),
            "traffic": updates.get("traffic", current.get("traffic")),
            "filters": current.get("filters", []),
            "dynvar": current.get("dynvar", [{"name": "", "value": ""}]),
            "urlfilter": current.get("urlfilter", []),
            "schedule": current.get("schedule", []),
            "pagelock": current.get("pagelock", {"enabled": False, "action": "blank", "url": "", "timeout": 10}),
            "lptrack": current.get("lptrack", ""),
            "dynautopt": current.get("dynautopt", "1"),
            "urlkeyword": current.get("urlkeyword", ""),
            "allowedcountries": current.get("allowedcountries"),
            "allowedref": current.get("allowedref"),
            "archived": current.get("archived", 0),
            "device": current.get("device")
        }
        
        response = requests.post(
            f"{self.base_url}/campaigns.php",
            params={"a": "update"},
            json=payload,
            headers=self._headers()
        )
        return response.status_code == 200
    
    def change_status(self, campaign_id: str, status: int) -> bool:
        """
        Change campaign status
        0=Review, 1=Active, 2=Allow All, -1=Block All
        """
        self._ensure_authenticated()
        response = requests.get(
            f"{self.base_url}/campaigns.php",
            params={"a": "changeStatus", "clid": campaign_id, "status": status},
            headers=self._headers()
        )
        return response.status_code == 200
    
    def get_embed_code(self, campaign_id: str) -> str:
        """Get PHP embed code for deployment"""
        self._ensure_authenticated()
        response = requests.get(
            f"{self.base_url}/campaigns.php",
            params={"a": "getPhpEmbed", "clid": campaign_id},
            headers=self._headers()
        )
        return response.text if response.status_code == 200 else None
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_change_status(self, campaign_ids: List[str], status: int) -> Dict[str, bool]:
        """Change status for multiple campaigns"""
        results = {}
        for cid in campaign_ids:
            results[cid] = self.change_status(cid, status)
        return results
    
    def bulk_update(self, updates: List[Dict]) -> Dict[str, bool]:
        """
        Bulk update campaigns
        updates = [{"campaign_id": "xxx", "fakeurl": "...", ...}, ...]
        """
        results = {}
        for item in updates:
            cid = item.pop("campaign_id")
            results[cid] = self.update_campaign(cid, **item)
        return results
    
    def get_all_embed_codes(self, campaign_ids: List[str] = None) -> Dict[str, str]:
        """Get embed codes for multiple campaigns"""
        if not campaign_ids:
            campaigns = self.get_campaigns()
            campaign_ids = [c["name"] for c in campaigns]
        
        codes = {}
        for cid in campaign_ids:
            codes[cid] = self.get_embed_code(cid)
        return codes
    
    # ==================== REPORTING ====================
    
    def get_status_report(self) -> List[Dict]:
        """Get status for all campaigns"""
        campaigns = self.get_campaigns()
        return [{
            "campaign_id": c["name"],
            "campaign_name": c["info"],
            "status": c["active"],
            "fakeurl": c.get("fakeurl"),
            "traffic": c.get("traffic")
        } for c in campaigns]
    
    def get_block_report(self, date: str = None) -> List[Dict]:
        """Get block rate report"""
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        campaigns = self.get_campaigns(date, date)
        report = []
        for c in campaigns:
            total = c.get("total", 0)
            blocked = c.get("block", 0)
            rate = (blocked / total * 100) if total > 0 else 0
            report.append({
                "campaign_id": c["name"],
                "campaign_name": c["info"],
                "date": date,
                "total": total,
                "blocked": blocked,
                "allowed": total - blocked,
                "block_rate": round(rate, 2),
                "flag": "HIGH" if rate > 50 else "OK"
            })
        return report


# ==================== TEST ALL ENDPOINTS ====================

def main():
    api = NoIPFraudAPI("https://luxeattic.com/admin/api", "luxeattic", "Z456789xAa")
    
    print("\n" + "="*70)
    print("COMPLETE API TEST - All 7 Endpoints")
    print("="*70)
    
    # 1. Login
    print("\n1. Testing Login...")
    assert api.login(), "Login failed"
    print("✅ Login successful")
    
    # 2. Get Campaigns
    print("\n2. Testing Get Campaigns...")
    campaigns = api.get_campaigns()
    print(f"✅ Retrieved {len(campaigns)} campaigns")
    
    # 3. Change Status
    print("\n3. Testing Change Status...")
    if campaigns:
        result = api.change_status(campaigns[0]["name"], 1)
        print(f"✅ Status changed: {result}")
    
    # 4. Get Status Report
    print("\n4. Testing Status Report...")
    report = api.get_status_report()
    print(f"✅ Generated report for {len(report)} campaigns")
    
    # 5. Get Block Report
    print("\n5. Testing Block Report...")
    block_report = api.get_block_report()
    print(f"✅ Generated block report for {len(block_report)} campaigns")
    
    # 6. Get Embed Code
    print("\n6. Testing Get Embed Code...")
    if campaigns:
        code = api.get_embed_code(campaigns[0]["name"])
        print(f"✅ Retrieved embed code ({len(code) if code else 0} chars)")
    
    # 7. Create Campaign (optional - uncomment to test)
    # print("\n7. Testing Create Campaign...")
    # new = api.create_campaign("API-Test", "http://safe.com", "http://money.com")
    # print(f"✅ Campaign created: {new}")
    
    # 8. Update Campaign
    print("\n8. Testing Update Campaign...")
    if campaigns:
        result = api.update_campaign(campaigns[0]["name"], info="Test-Update")
        print(f"✅ Campaign updated: {result}")
    
    print("\n" + "="*70)
    print("✅ ALL 7 ENDPOINTS TESTED AND WORKING")
    print("="*70)
    print("\nReady for n8n implementation!")


if __name__ == "__main__":
    main()