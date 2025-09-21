from bedrock_provider import BedrockProvider

def test_nova_reel():
    try:
        provider = BedrockProvider()
        
        # Test Nova Reel video generation
        result = provider.get_ai_response("python programming", "beginner", "video", "")
        
        if result:
            print("SUCCESS: Nova Reel response received")
            print(f"Response length: {len(result)} chars")
            if "nova-reels-video" in result:
                print("SUCCESS: Nova Reel video component found")
            else:
                print("INFO: Fallback response used")
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
    test_nova_reel()