#!/usr/bin/env python3
"""
Test SFTP connection to noIPFraud servers
"""

import paramiko
import stat
from pathlib import Path

# Server configs
SERVERS = {
    "luxeattic": {
        "host": "13.229.117.189",
        "port": 22,
        "username": "ubuntu",
        "key_file": "luxeattic.pem",
        "auth_type": "key"
    },
    "kinthaifood": {
        "host": "47.128.80.134",
        "port": 22,
        "username": "ubuntu",
        "key_file": "th02.pem",
        "auth_type": "key"
    },
    "techsmartdevice": {
        "host": "18.143.171.57",
        "port": 22,
        "username": "ubuntu",
        "key_file": "th03.pem",
        "auth_type": "key"
    }
}


def test_sftp_connection(server_name, config):
    """Test SFTP connection and list files"""
    
    print(f"\n{'='*70}")
    print(f"Testing: {server_name}")
    print(f"Host: {config['host']}:{config['port']}")
    print(f"{'='*70}")
    
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect with key file
        print(f"Connecting with key file: {config['key_file']}")
        if not Path(config['key_file']).exists():
            print(f"❌ Key file not found: {config['key_file']}")
            return False
        
        # Load private key
        try:
            pkey = paramiko.RSAKey.from_private_key_file(config['key_file'])
        except Exception as e:
            try:
                pkey = paramiko.Ed25519Key.from_private_key_file(config['key_file'])
            except Exception as e2:
                print(f"❌ Could not load key: {e}")
                return False
        
        ssh.connect(
            hostname=config["host"],
            port=config["port"],
            username=config["username"],
            pkey=pkey,
            look_for_keys=False,
            allow_agent=False
        )
        
        print("✅ SSH connected")
        
        # Open SFTP
        sftp = ssh.open_sftp()
        print("✅ SFTP session opened")
        
        # List root directory
        print("\n📂 Root directory contents:")
        try:
            files = sftp.listdir('.')
            for f in files[:10]:  # Show first 10
                try:
                    attrs = sftp.stat(f)
                    is_dir = stat.S_ISDIR(attrs.st_mode)
                    icon = "📁" if is_dir else "📄"
                    print(f"   {icon} {f}")
                except:
                    print(f"   ? {f}")
        except Exception as e:
            print(f"   Could not list root: {e}")
        
        # Try common web paths
        web_paths = [
            '/var/www/html',
            '/var/www',
            '/public_html',
            '/home/ubuntu/public_html',
            '/usr/share/nginx/html'
        ]
        
        print("\n🔍 Searching for web files...")
        for path in web_paths:
            try:
                files = sftp.listdir(path)
                print(f"\n✅ Found: {path}")
                print(f"   Files: {len(files)} items")
                
                # Show PHP files
                php_files = [f for f in files if f.endswith('.php')]
                if php_files:
                    print(f"   PHP files found: {len(php_files)}")
                    for php in php_files[:5]:
                        print(f"      📄 {php}")
                break
            except:
                continue
        
        # Close connections
        sftp.close()
        ssh.close()
        
        print(f"\n✅ {server_name}: Connection successful!")
        return True
        
    except paramiko.AuthenticationException:
        print(f"❌ Authentication failed")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "="*70)
    print("noIPFraud SFTP Connection Test")
    print("="*70)
    
    results = {}
    
    # Test all servers
    for server_name, config in SERVERS.items():
        results[server_name] = test_sftp_connection(server_name, config)
        print("\n")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for server, success in results.items():
        status = "✅ Connected" if success else "❌ Failed"
        print(f"{server}: {status}")


if __name__ == "__main__":
    # Check if paramiko is installed
    try:
        import paramiko
    except ImportError:
        print("❌ paramiko not installed")
        print("Run: pip install paramiko")
        exit(1)
    
    main()