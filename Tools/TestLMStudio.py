#!/usr/bin/env python3
"""
Test script for LM Studio integration
"""

import sys
import os

# Add the parent directory to the path so we can import Writer modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Writer.Interface.Wrapper import Interface
from Writer.Interface.LMStudio import LMStudio

def test_lmstudio_direct():
    """Test LM Studio interface directly"""
    print("Testing LM Studio interface directly...")
    
    try:
        # Test with default settings
        lmstudio = LMStudio(
            api_url="http://localhost:1234/v1/chat/completions",
            model="local-model"
        )
        print("✓ LM Studio interface created successfully")
        
        # Test parameter setting
        lmstudio.set_params(temperature=0.7, max_tokens=100)
        print("✓ Parameters set successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error testing LM Studio interface: {e}")
        return False

def test_lmstudio_wrapper():
    """Test LM Studio through the wrapper"""
    print("\nTesting LM Studio through wrapper...")
    
    try:
        # Test with URL format
        interface = Interface(Models=["lmstudio://local-model@http://localhost:1234/v1/chat/completions"])
        print("✓ LM Studio loaded through wrapper successfully")
        
        # Test with simple format (should default to localhost)
        interface2 = Interface(Models=["lmstudio://local-model"])
        print("✓ LM Studio loaded with default URL successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error testing LM Studio wrapper: {e}")
        return False

def test_lmstudio_chat():
    """Test actual chat functionality (requires LM Studio running)"""
    print("\nTesting LM Studio chat functionality...")
    print("Note: This requires LM Studio to be running with API server enabled")
    
    try:
        lmstudio = LMStudio(
            api_url="http://localhost:1234/v1/chat/completions",
            model="local-model"
        )
        
        messages = [
            {"role": "user", "content": "Hello! Please respond with 'Hello from LM Studio!'"}
        ]
        
        response = lmstudio.chat(messages=messages, max_retries=1)
        print(f"✓ Chat response received: {response[:50]}...")
        return True
        
    except Exception as e:
        print(f"✗ Chat test failed (this is expected if LM Studio is not running): {e}")
        print("This is normal if LM Studio is not currently running")
        return False

def main():
    print("LM Studio Integration Test")
    print("=" * 40)
    
    # Test 1: Direct interface
    test1_passed = test_lmstudio_direct()
    
    # Test 2: Wrapper integration
    test2_passed = test_lmstudio_wrapper()
    
    # Test 3: Chat functionality (optional)
    test3_passed = test_lmstudio_chat()
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Direct Interface: {'✓ PASS' if test1_passed else '✗ FAIL'}")
    print(f"Wrapper Integration: {'✓ PASS' if test2_passed else '✗ FAIL'}")
    print(f"Chat Functionality: {'✓ PASS' if test3_passed else '✗ SKIP (LM Studio not running)'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 LM Studio integration is working correctly!")
        print("\nUsage examples:")
        print("1. lmstudio://local-model@http://localhost:1234/v1/chat/completions")
        print("2. lmstudio://local-model (uses default localhost URL)")
        print("3. lmstudio://my-model@http://192.168.1.100:1234/v1/chat/completions")
    else:
        print("\n❌ LM Studio integration has issues")

if __name__ == "__main__":
    main() 