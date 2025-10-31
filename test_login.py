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


def main():
    """
    Main function to run the test
    """
    print("\n")
    print("*"*70)
    print("*" + " "*68 + "*")
    print("*" + "  noIPFraud API Testing - Login Endpoint".center(68) + "*")
    print("*" + " "*68 + "*")
    print("*"*70)
    print("\n")
    
    # Run login test
    result = login()
    
    print("\n\n")
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if result and AUTH_TOKEN:
        print("✅ Status: SUCCESS")
        print(f"✅ Token received: Yes")
        print(f"✅ Token stored: Yes")
        print(f"\n🔑 Full Token:\n{AUTH_TOKEN}")
        print("\n" + "="*70)
        print("✨ NEXT STEP: We can now test other API endpoints!")
        print("="*70)
    else:
        print("❌ Status: FAILED")
        print("❌ Token received: No")
        print("\n💡 Possible issues:")
        print("   - Check internet connection")
        print("   - Verify credentials are correct")
        print("   - Check if the API endpoint URL is correct")
        print("="*70)


if __name__ == "__main__":
    main()