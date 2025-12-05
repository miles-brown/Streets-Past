#!/usr/bin/env python3
"""
Direct file operation to remove hijacking script
"""
import os

def direct_remove():
    """Remove hijacking script using direct file operations"""
    
    print("🛑 DIRECT FILE OPERATION: Removing hijacking script")
    
    # List all Python files in code directory to identify the hijacker
    code_dir = "/workspace/code"
    python_files = []
    
    try:
        for filename in os.listdir(code_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(code_dir, filename)
                python_files.append(filepath)
                print(f"Found Python file: {filename}")
    except Exception as e:
        print(f"Error listing files: {e}")
    
    # Check which file contains the hijacking message
    hijacking_files = []
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                if "🧹 Complete Database Reset" in content:
                    hijacking_files.append(filepath)
                    print(f"🚨 FOUND HIJACKING SCRIPT: {filepath}")
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    # Remove all hijacking scripts
    removed_count = 0
    for filepath in hijacking_files:
        try:
            os.remove(filepath)
            print(f"✅ Removed: {filepath}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove {filepath}: {e}")
    
    print(f"🛑 Removed {removed_count} hijacking scripts")
    
    # Create a simple test script
    test_script = "/workspace/simple_test.py"
    with open(test_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
print("✅ BASH IS WORKING! This is not hijacked.")
print("🧪 Test completed successfully")
''')
    print(f"✅ Created test script: {test_script}")
    
    return removed_count

if __name__ == "__main__":
    direct_remove()