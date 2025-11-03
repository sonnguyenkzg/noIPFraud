#!/usr/bin/env python3
"""noIPFraud - Update Campaign Test"""

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


def get_campaigns():
    """Get current campaigns"""
    url = f"{BASE_URL}/campaigns.php"
    params = {"a": "list", "from": "2025-10-31", "to": "2025-10-31"}
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    response = requests.get(url, params=params, headers=headers)
    return response.json() if response.status_code == 200 else []


def update_campaign(campaign_id, **updates):
    """
    Update an existing campaign
    
    Args:
        campaign_id: Campaign ID (e.g., 'twvpck0j')
        **updates: Fields to update (info, fakeurl, realurl, rules, etc.)
    """
    url = f"{BASE_URL}/campaigns.php"
    params = {"a": "update"}
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Get current campaign data first
    campaigns = get_campaigns()
    current = next((c for c in campaigns if c["name"] == campaign_id), None)
    
    if not current:
        print(f"❌ Campaign {campaign_id} not found")
        return None
    
    # Merge current data with updates
    payload = {
        "name": campaign_id,
        "cv": current.get("cv", "1.8.2"),
        "maxrisk": current.get("maxrisk"),
        "info": updates.get("info", current.get("info")),
        "active": updates.get("active", current.get("active")),
        "allowedcountries": current.get("allowedcountries"),
        "allowedref": current.get("allowedref"),
        "archived": current.get("archived", 0),
        "device": current.get("device"),
        "dynautopt": updates.get("dynautopt", current.get("dynautopt", "1")),
        "dynvar": updates.get("dynvar", current.get("dynvar", [{"name": "", "value": ""}])),
        "fakeurl": updates.get("fakeurl", current.get("fakeurl")),
        "filters": updates.get("filters", current.get("filters", [])),
        "lptrack": updates.get("lptrack", current.get("lptrack", "")),
        "maxrisk": current.get("maxrisk"),
        "pagelock": updates.get("pagelock", current.get("pagelock", {
            "enabled": False,
            "action": "blank",
            "url": "",
            "timeout": 10
        })),
        "realurl": updates.get("realurl", current.get("realurl")),
        "rules": updates.get("rules", current.get("rules")),
        "schedule": updates.get("schedule", current.get("schedule", [])),
        "traffic": updates.get("traffic", current.get("traffic")),
        "urlfilter": updates.get("urlfilter", current.get("urlfilter", [{"variable": "", "action": "1", "value": ""}])),
        "urlkeyword": updates.get("urlkeyword", current.get("urlkeyword", ""))
    }
    
    print(f"\n{'='*70}")
    print(f"Updating campaign: {campaign_id}")
    print(f"{'='*70}")
    print(f"Updates: {json.dumps(updates, indent=2)}")
    
    try:
        response = requests.post(url, params=params, json=payload, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print(f"\n✅ Campaign updated successfully!")
            return response.json()
        else:
            print(f"\n❌ Failed to update campaign")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("\nnoIPFraud - Update Campaign Test\n")
    
    if not login():
        return
    
    # Get campaigns
    campaigns = get_campaigns()
    if not campaigns:
        print("No campaigns found")
        return
    
    # Use first campaign for testing
    test_campaign = campaigns[0]["name"]
    print(f"Testing with campaign: {test_campaign} ({campaigns[0]['info']})")
    
    # Test 1: Update campaign name
    print("\n\nTEST 1: Update campaign name")
    update_campaign(
        test_campaign,
        info="Updated-Test-Name"
    )
    
    # Test 2: Update URLs
    print("\n\nTEST 2: Update safe and money URLs")
    update_campaign(
        test_campaign,
        fakeurl="http://newsafepage.com",
        realurl=[{
            "url": "http://newmoneypage.com",
            "perc": 100,
            "desc": "Updated LP"
        }]
    )
    
    # Test 3: Update country filter
    print("\n\nTEST 3: Update country filter")
    update_campaign(
        test_campaign,
        rules={
            "mobile": {"allow": True, "d": []},
            "country": {"allow": True, "d": ["th", "vn", "my"]}
        }
    )
    
    print(f"\n{'='*70}")
    print("✅ ALL UPDATE TESTS COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()