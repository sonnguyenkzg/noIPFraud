#!/usr/bin/env python3
"""
noIPFraud API Testing Script
Test the login endpoint step by step
"""

import requests
import json
from datetime import datetime


# Configuration
BASE_URL = "https://luxeattic.com/admin/api"
USERNAME = "luxeattic"
PASSWORD = "Z456789xAa"

# Global variable to store token
AUTH_TOKEN = None


def login():
    """
    Login to noIPFraud and get authentication token
    """
    global AUTH_TOKEN
    
    url = f"{BASE_URL}/login.php?a=auth"
    
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("="*70)
    print("🔐 TESTING LOGIN ENDPOINT")
    print("="*70)
    print(f"\n📍 URL: {url}")
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    print("\n" + "="*70 + "\n")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # Print response details
        print(f"✅ Status Code: {response.status_code}")
        print(f"\n📥 Response Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        print("\n" + "="*70)
        print("📥 RESPONSE BODY:")
        print("="*70 + "\n")
        
        # Try to parse as JSON
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
            
            # Store token if successful
            if "token" in response_json:
                AUTH_TOKEN = response_json["token"]
                print("\n" + "="*70)
                print("🎉 SUCCESS! Token received and stored.")
                print("="*70)
                print(f"🔑 Token (first 50 chars): {AUTH_TOKEN[:50]}...")
                print(f"📏 Token Length: {len(AUTH_TOKEN)} characters")
                print("="*70)
                return response_json
            else:
                print("\n⚠️  Warning: Response doesn't contain 'token' field")
                return response_json
                
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON:")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error occurred: {e}")
        return None


def get_campaigns():
    """
    Get list of campaigns using the authenticated token
    """
    if not AUTH_TOKEN:
        print("❌ No auth token available. Please login first!")
        return None
    
    # Use today's date for the date range
    today = datetime.now().strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/campaigns.php"
    
    params = {
        "a": "list",
        "from": today,
        "to": today
    }
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    print("="*70)
    print("📋 TESTING GET CAMPAIGNS ENDPOINT")
    print("="*70)
    print(f"\n📍 URL: {url}")
    print(f"📋 Query Params: {params}")
    print(f"🔑 Authorization: Bearer {AUTH_TOKEN[:50]}...")
    print("\n" + "="*70 + "\n")
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        print(f"✅ Status Code: {response.status_code}")
        print("\n" + "="*70)
        print("📥 RESPONSE BODY:")
        print("="*70 + "\n")
        
        try:
            response_json = response.json()
            
            # Pretty print with limited depth for readability
            if isinstance(response_json, list):
                print(f"📊 Total Campaigns Found: {len(response_json)}")
                print("\n" + "-"*70 + "\n")
                
                # Show first 3 campaigns in detail
                for i, campaign in enumerate(response_json[:3]):
                    print(f"Campaign {i+1}:")
                    print(json.dumps(campaign, indent=2))
                    print("\n" + "-"*70 + "\n")
                
                if len(response_json) > 3:
                    print(f"... and {len(response_json) - 3} more campaigns")
                
                print("\n" + "="*70)
                print("🎉 SUCCESS! Campaign list retrieved.")
                print("="*70)
                return response_json
            else:
                print(json.dumps(response_json, indent=2))
                return response_json
                
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON:")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error occurred: {e}")
        return None


def main():
    """
    Main function to run the test
    """
    print("\n")
    print("*"*70)
    print("*" + " "*68 + "*")
    print("*" + "  noIPFraud API Testing - Step by Step".center(68) + "*")
    print("*" + " "*68 + "*")
    print("*"*70)
    print("\n")
    
    # Step 1: Login
    print("STEP 1: Testing Login\n")
    login_result = login()
    
    if not login_result or not AUTH_TOKEN:
        print("\n❌ Login failed. Cannot proceed to next steps.")
        return
    
    print("\n" + "="*70)
    print("✅ STEP 1 COMPLETE - Login Successful!")
    print("="*70)
    
    # Step 2: Get Campaigns
    print("\n\n")
    input("Press Enter to continue to Step 2 (Get Campaigns)...")
    print("\n")
    
    print("STEP 2: Testing Get Campaigns\n")
    campaigns = get_campaigns()
    
    if campaigns:
        print("\n" + "="*70)
        print("✅ STEP 2 COMPLETE - Campaigns Retrieved!")
        print("="*70)
    else:
        print("\n❌ Failed to retrieve campaigns")
    
    print("\n\n")
    print("="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"✅ Login: {'SUCCESS' if AUTH_TOKEN else 'FAILED'}")
    print(f"✅ Get Campaigns: {'SUCCESS' if campaigns else 'FAILED'}")
    
    if AUTH_TOKEN and campaigns:
        print("\n✨ Next steps available:")
        print("   - Test updating a campaign")
        print("   - Test creating a campaign")
        print("   - Test getting campaign stats")
        print("   - Test changing campaign status")
    
    print("="*70)


if __name__ == "__main__":
    main()