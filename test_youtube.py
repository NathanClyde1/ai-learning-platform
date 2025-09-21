from bedrock_provider import BedrockProvider

def test_youtube_video():
    try:
        provider = BedrockProvider()
        
        # Test video format specifically
        result = provider.get_ai_response("python programming", "beginner", "video", "")
        
        if result and "youtube.com/embed/" in result:
            print("SUCCESS: YouTube video embedded")
            print(f"Response contains video embed: {len(result)} chars")
            return True
        elif result:
            print("WARNING: Got response but no video embed")
            print(f"Response preview: {result[:200]}...")
            return False
        else:
            print("ERROR: Got empty response")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_youtube_video()