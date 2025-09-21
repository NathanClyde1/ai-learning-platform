from bedrock_provider import BedrockProvider

def test_nova_canvas():
    try:
        provider = BedrockProvider()
        
        # Test Nova Canvas image generation
        result = provider.get_ai_response("solar system", "beginner", "sketch", "")
        
        if result:
            print("SUCCESS: Nova Canvas response received")
            print(f"Response length: {len(result)} chars")
            if "nova-canvas" in result:
                print("SUCCESS: Nova Canvas image component found")
            else:
                print("INFO: Standard sketch response used")
            return True
        else:
            print("ERROR: No response received")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_nova_canvas()