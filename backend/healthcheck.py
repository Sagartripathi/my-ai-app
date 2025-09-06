#!/usr/bin/env python3
import urllib.request
import urllib.error
import sys
import time

def health_check():
    try:
        # Try to connect to the health endpoint
        response = urllib.request.urlopen('http://localhost:8000/health', timeout=10)
        if response.getcode() == 200:
            print("Health check passed")
            return True
        else:
            print(f"Health check failed with status code: {response.getcode()}")
            return False
    except urllib.error.URLError as e:
        print(f"Health check failed with URL error: {e}")
        return False
    except Exception as e:
        print(f"Health check failed with error: {e}")
        return False

if __name__ == "__main__":
    if health_check():
        sys.exit(0)
    else:
        sys.exit(1)
