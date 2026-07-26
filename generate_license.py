#!/usr/bin/env python3
"""
Pro Access BD - License Key Generator
Generates cryptographically signed license keys for the Lovable Pro extension/plugin.
"""

import sys
import time
import json
import base64
import hmac
import hashlib
import argparse

# Secret XOR reconstruction components matching license-system.js
_K = 'T3chV3rs3-X'
_P1 = [0x17,0x56,0x44,0x34,0x6b,0x1d,0x2a,0x7a,0x50,0x33,0x56,0x3c,0x7b,0x56,0x74,0x7c,0x3b,0x72,0x68,0x2a,0x15,0x12,0x3f,0x34,0x1d,0x52,0x1b,0x59,0x72,0x50,0x29,0x21]
_P2 = [0x37,0x5e,0x59,0x44,0x73,0x1e,0x0a,0x7a,0x63,0x54,0x34,0x28,0x5a,0x6a,0x44,0x73,0x37,0x29,0x6b,0x25,0x7b,0x77,0x5f,0x6b,0x5a,0x3b,0x62,0x7a,0x57,0x2a,0x4e,0x4b]

def get_license_secret() -> bytes:
    """Reconstructs the secret key used for signing HMAC SHA-256 signatures."""
    def _d(a, k):
        return ''.join(chr(a[i] ^ ord(k[i % len(k)])) for i in range(len(a)))
    secret_str = _d(_P1, _K) + _d(_P2, _K)
    return secret_str.encode('utf-8')

def generate_key(license_type: str = 'lifetime', email: str = 'user@proaccess.bd', custom_days: int = None, custom_hours: int = None, custom_minutes: int = None) -> str:
    """
    Generates a signed license key string for the given license type and email.
    
    Types supported:
      - 'lifetime' or 'Lifetime'
      - '1year', '365d', '1 Year'
      - '1month', '30d', '30days', '1 Month'
      - '15m', '30m' (minutes)
      - '1h', '2h', '6h', '12h' (hours)
      - custom_days, custom_hours, custom_minutes
    """
    issued = int(time.time() * 1000)
    l_type_lower = str(license_type).lower().strip()
    
    if l_type_lower in ['lifetime', 'life', '1']:
        expires = 'lifetime'
        type_label = 'Lifetime'
        dur_code = 'LIFETIME'
    elif l_type_lower in ['1year', '1 year', '365d', 'year', '2']:
        expires = issued + (365 * 24 * 60 * 60 * 1000)
        type_label = '1 Year'
        dur_code = '1YEAR'
    elif l_type_lower in ['1month', '1 month', '30d', '30days', 'month', '3']:
        expires = issued + (30 * 24 * 60 * 60 * 1000)
        type_label = '30 Days'
        dur_code = '1MONTH'
    elif custom_minutes is not None or (l_type_lower.endswith('m') and not l_type_lower.endswith('month')) or l_type_lower.endswith('min') or l_type_lower.endswith('mins') or l_type_lower.endswith('minutes'):
        try:
            if custom_minutes is not None:
                mins = custom_minutes
            else:
                clean_m = l_type_lower.replace('minutes', '').replace('minute', '').replace('mins', '').replace('min', '').replace('m', '')
                mins = int(clean_m)
        except ValueError:
            mins = 15
        expires = issued + (mins * 60 * 1000)
        type_label = f'{mins} Mins (Trial)'
        dur_code = f'{mins}M'
    elif custom_hours is not None or l_type_lower.endswith('h') or l_type_lower.endswith('hr') or l_type_lower.endswith('hrs') or l_type_lower.endswith('hours'):
        try:
            if custom_hours is not None:
                hrs = custom_hours
            else:
                clean_h = l_type_lower.replace('hours', '').replace('hour', '').replace('hrs', '').replace('hr', '').replace('h', '')
                hrs = int(clean_h)
        except ValueError:
            hrs = 1
        expires = issued + (hrs * 60 * 60 * 1000)
        type_label = f"{hrs} Hour{'s' if hrs > 1 else ''} (Trial)"
        dur_code = f'{hrs}H'
    elif custom_days is not None or l_type_lower.endswith('d') or l_type_lower.endswith('days'):
        try:
            if custom_days is not None:
                days = custom_days
            else:
                clean_d = l_type_lower.replace('days', '').replace('day', '').replace('d', '')
                days = int(clean_d)
        except ValueError:
            days = 30
        expires = issued + (days * 24 * 60 * 60 * 1000)
        type_label = f'{days} Days'
        dur_code = f'{days}DAYS'
    else:
        expires = 'lifetime'
        type_label = 'Lifetime'
        dur_code = 'LIFETIME'

    raw_payload = f"{email}:{issued}:{expires}".encode('utf-8')
    secret = get_license_secret()
    signature_hex = hmac.new(secret, raw_payload, hashlib.sha256).hexdigest().upper()
    
    code1 = signature_hex[:4]
    code2 = signature_hex[4:8]
    
    return f"LOVABLE-PRO-{dur_code}-{code1}-{code2}"

def interactive_menu():
    print("=" * 60)
    print("   PRO ACCESS BD - LOVABLE EXTENSION LICENSE GENERATOR")
    print("=" * 60)
    print("\nSelect License Type:")
    print("  [1] Lifetime Access")
    print("  [2] 1 Year Access (365 Days)")
    print("  [3] 30 Days Access (1 Month)")
    print("  [4] Custom Days")
    print("  [5] Trial Access (Hours)")
    print("  [6] Trial Access (Minutes)")
    
    choice = input("\nEnter choice (1-6) [default: 1]: ").strip() or "1"
    
    custom_days = None
    custom_hours = None
    custom_minutes = None
    if choice == "1":
        license_type = "lifetime"
    elif choice == "2":
        license_type = "1year"
    elif choice == "3":
        license_type = "30d"
    elif choice == "4":
        license_type = "custom_days"
        try:
            custom_days = int(input("Enter number of days: ").strip())
        except ValueError:
            print("Invalid input. Defaulting to 30 days.")
            custom_days = 30
    elif choice == "5":
        license_type = "custom_hours"
        try:
            custom_hours = int(input("Enter number of hours (e.g. 1, 2, 6, 12): ").strip())
        except ValueError:
            print("Invalid input. Defaulting to 1 hour.")
            custom_hours = 1
    elif choice == "6":
        license_type = "custom_minutes"
        try:
            custom_minutes = int(input("Enter number of minutes (e.g. 15, 30, 45): ").strip())
        except ValueError:
            print("Invalid input. Defaulting to 15 minutes.")
            custom_minutes = 15
    else:
        license_type = "lifetime"

    email = input("\nEnter user email/identifier [default: user@proaccess.bd]: ").strip() or "user@proaccess.bd"
    
    try:
        count = int(input("\nHow many keys to generate? [default: 1]: ").strip() or "1")
    except ValueError:
        count = 1

    print("\n" + "-" * 60)
    print(f"Generating {count} key(s)...")
    print("-" * 60 + "\n")

    keys = []
    for i in range(count):
        key = generate_key(license_type, email, custom_days, custom_hours, custom_minutes)
        keys.append(key)
        print(f"Key #{i+1}:\n{key}\n")

    print("-" * 60)
    print("Success! Copy and paste the license key into the extension activation box.")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Generate license keys for Lovable Pro Extension.")
    parser.add_argument("-t", "--type", choices=["lifetime", "1year", "1month"], help="License duration type")
    parser.add_argument("-d", "--days", type=int, help="Custom duration in days")
    parser.add_argument("-e", "--email", type=str, default="user@proaccess.bd", help="User email or identifier")
    parser.add_argument("-c", "--count", type=int, default=1, help="Number of keys to generate")
    parser.add_argument("-o", "--output", type=str, help="Output file path to save keys")

    args = parser.parse_args()

    # If no CLI arguments provided, launch interactive menu
    if len(sys.argv) == 1:
        interactive_menu()
        return

    l_type = args.type or ("custom" if args.days else "lifetime")
    keys = [generate_key(l_type, args.email, args.days) for _ in range(args.count)]

    if args.output:
        with open(args.output, "w") as f:
            for k in keys:
                f.write(k + "\n")
        print(f"Saved {len(keys)} key(s) to {args.output}")
    else:
        for i, k in enumerate(keys, 1):
            if args.count > 1:
                print(f"Key #{i}:")
            print(k)

if __name__ == "__main__":
    main()
