import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.core.factory import create_app
    from backend.models import *
    from backend.database.session import engine
    from backend.database.base import Base
    
    # Try to create tables in sqlite
    Base.metadata.create_all(bind=engine)
    print("Successfully imported models and created tables!")
except Exception as e:
    print(f"Error: {e}")
