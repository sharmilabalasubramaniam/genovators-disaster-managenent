import os

def compare_faces(image_a_url: str, image_b_url: str) -> float:
    """
    Compare two faces using DeepFace (embedding-based comparison).
    Returns a similarity score between 0.0 and 1.0.
    """
    if not image_a_url or not image_b_url:
        return None
        
    try:
        from deepface import DeepFace
        import urllib.request
        import tempfile
        import shutil
        
        # Helper to get local path for URL or local file
        def get_local_path(url_or_path):
            if url_or_path.startswith('http'):
                # Handle our local /api/uploads/ URLs by converting to local path
                if 'api/uploads/' in url_or_path:
                    filename = url_or_path.split('/')[-1]
                    local_path = os.path.join("uploads", filename)
                    if os.path.exists(local_path):
                        return local_path
                        
                # Download external URL to temp file
                ext = url_or_path.split('.')[-1]
                if len(ext) > 4: ext = 'jpg'
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
                with urllib.request.urlopen(url_or_path) as response, open(temp_file.name, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                return temp_file.name
            return url_or_path

        path_a = get_local_path(image_a_url)
        path_b = get_local_path(image_b_url)
        
        if not os.path.exists(path_a) or not os.path.exists(path_b):
            return None

        # Run embedding-based verification
        result = DeepFace.verify(
            img1_path=path_a, 
            img2_path=path_b, 
            model_name="Facenet512", # Lightweight, robust embedding model
            enforce_detection=False # Don't crash if face is slightly occluded
        )
        
        # Clean up temp files if we created them
        if path_a.startswith(tempfile.gettempdir()): os.remove(path_a)
        if path_b.startswith(tempfile.gettempdir()): os.remove(path_b)
        
        # Deepface returns distance, we convert to similarity score
        # Lower distance = higher similarity
        distance = result.get("distance", 1.0)
        similarity = max(0.0, 1.0 - distance)
        
        # If it says they are verified, boost the score
        if result.get("verified"):
            return max(similarity, 0.85)
            
        return similarity
        
    except ImportError:
        print("DeepFace not installed.")
        return None
    except ValueError as e:
        if "Face could not be detected" in str(e):
            print("No face detected.")
            return None
        return None
    except Exception as e:
        print(f"Face matching error: {e}")
        return None
