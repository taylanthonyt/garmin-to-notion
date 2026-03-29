import os
import pickle
from pathlib import Path
from garminconnect import Garmin as GarminClient
from dotenv import load_dotenv

# Cache location for storing authenticated session
SESSION_CACHE_FILE = Path("/tmp/garmin_session.pkl")

def save_session(garmin_client: GarminClient) -> None:
    """Save the authenticated Garmin client session to a file."""
    try:
        with open(SESSION_CACHE_FILE, 'wb') as f:
            pickle.dump(garmin_client, f)
    except Exception as e:
        print(f"Warning: Could not save Garmin session: {e}")

def load_session() -> GarminClient | None:
    """Load a previously authenticated Garmin client session from file."""
    if SESSION_CACHE_FILE.exists():
        try:
            with open(SESSION_CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Warning: Could not load Garmin session: {e}")
            SESSION_CACHE_FILE.unlink(missing_ok=True)
    return None

def get_garmin_client(force_login: bool = False) -> GarminClient:
    """
    Get an authenticated Garmin client. Reuses existing session if available.
    
    Args:
        force_login: If True, always create a new login session
    
    Returns:
        An authenticated GarminClient instance
    """
    load_dotenv()
    
    # Try to load cached session
    if not force_login:
        cached_client = load_session()
        if cached_client:
            try:
                # Verify the session is still valid by making a simple request
                cached_client.get_user_summary()
                return cached_client
            except Exception as e:
                print(f"Cached session expired: {e}")
                SESSION_CACHE_FILE.unlink(missing_ok=True)
    
    # Create new session
    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    
    garmin_client = GarminClient(garmin_email, garmin_password)
    garmin_client.login()
    
    # Cache the authenticated session
    save_session(garmin_client)
    
    return garmin_client

def clear_session() -> None:
    """Clear the cached Garmin session."""
    SESSION_CACHE_FILE.unlink(missing_ok=True)