#!/usr/bin/env python3
"""
Final test runner - Execute the minimal test directly
"""
import sys
sys.path.append('/workspace/code')

# Import and run the test function
try:
    import minimal_test_import
    minimal_test_import.test_import_10_records()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
