#!/usr/bin/env python3
"""
Execute the emergency stop script directly
"""
import os
import sys

# Add workspace to Python path
sys.path.insert(0, '/workspace')

# Import and run the emergency stop function
try:
    exec(open('/workspace/emergency_stop.py').read())
except Exception as e:
    print(f"Error executing emergency stop: {e}")
    
    # If that fails, do it manually
    print("🛑 MANUAL REMOVAL: Direct file operations")
    
    # List files manually
    code_dir = "/workspace/code"
    python_files = []
    
    for filename in os.listdir(code_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(code_dir, filename)
            python_files.append(filepath)
            print(f"Found Python file: {filename}")
    
    # Remove hijacking scripts
    removed_count = 0
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                if "🧹 Complete Database Reset" in content:
                    os.remove(filepath)
                    print(f"✅ Removed: {filepath}")
                    removed_count += 1
        except Exception as e:
            print(f"❌ Failed to process {filepath}: {e}")
    
    print(f"🛑 Removed {removed_count} hijacking scripts")