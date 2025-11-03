#!/usr/bin/env python3
"""
noIPFraud - Create Campaign Test
"""

import requests
import json

BASE_URL = "https://luxeattic.com/admin/api"
USERNAME = "luxeattic"
PASSWORD = "Z456789xAa"
AUTH_TOKEN = None


def login():
    global AUTH_TOKEN
    url = f"{BASE_URL}/login.php?a=auth"
    response = requests.post(url, json={"username": USERNAME, "password": PASSWORD})
    if response.status_code == 200:
        AUTH_TOKEN = response.json()["token"]
        print(f"✅ Login successful")
        return True
    return False


def create_campaign(
    campaign_name: str,
    safe_url: str,
    money_url: str,
    traffic_source: str = "54218f34454c61f813000001",
    countries: list = None,
    mobile_only: bool = True
):
    """
    Create a new campaign
    
    Args:
        campaign_name: Display name for campaign
        safe_url: Safe page URL (fakeurl)
        money_url: Money side URL (realurl)
        traffic_source: Traffic source ID (default is Facebook)
        countries: List of country codes (e.g., ["th", "vn"])
        mobile_only: If True, allow mobile only
    """
    if countries is None:
        countries = ["th"]
    
    url = f"{BASE_URL}/campaigns.php"
    params = {"a": "create"}
    
    payload = {
        "info": campaign_name,
        "fakeurl": safe_url,
        "active": 0,  # Start as "Under Review"
        "dynautopt": True,
        "dynvar": [{"name": "", "value": ""}],
        "fakeurl1": safe_url,
        "filters": [],
        "info": campaign_name,
        "lptrack": False,
        "pagelock": {
            "enabled": False,
            "action": "blank",
            "url": "",
            "timeout": 10
        },
        "realurl": [{
            "url": money_url,
            "perc": 100,
            "desc": "LP1"
        }],
        "rules": {
            "mobile": {
                "allow": True,
                "d": [] if mobile_only else None
            },
            "country": {
                "allow": True,
                "d": countries
            }
        },
        "schedule": [],
        "traffic": traffic_source,
        "urlfilter": [{"variable": "", "action": "1", "value": ""}],
        "urlkeyword": ""
    }
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*70}")
    print(f"Creating campaign: {campaign_name}")
    print(f"{'='*70}")
    print(f"Safe URL: {safe_url}")
    print(f"Money URL: {money_url}")
    print(f"Countries: {countries}")
    print(f"Mobile only: {mobile_only}")
    
    try:
        response = requests.post(url, params=params, json=payload, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Campaign created successfully!")
            if isinstance(result, dict) and "name" in result:
                print(f"Campaign ID: {result['name']}")
            return result
        else:
            print(f"\n❌ Failed to create campaign")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("\nnoIPFraud - Create Campaign Test\n")
    
    if not login():
        return
    
    # Test creating a campaign
    result = create_campaign(
        campaign_name="Test-Campaign-API",
        safe_url="http://safepage.com=blocked",
        money_url="http://moneyside.com",
        countries=["th"],
        mobile_only=True
    )
    
    if result:
        print(f"\n{'='*70}")
        print("✅ TEST COMPLETE - Campaign Creation Works!")
        print(f"{'='*70}")
    else:
        print(f"\n{'='*70}")
        print("❌ TEST FAILED")
        print(f"{'='*70}")


if __name__ == "__main__":
    main()