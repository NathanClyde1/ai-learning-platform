from bedrock_provider import BedrockProvider

def test_learn_function():
    try:
        provider = BedrockProvider()
        
        # Test the same call that Flask makes
        result = provider.get_ai_response("python", "beginner", "chat", "")
        
        if result:
            print(f"SUCCESS: Got response ({len(result)} chars)")
            print(f"Response preview: {result[:100]}...")
            return True
        else:
            print("ERROR: Got empty response")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_learn_function()