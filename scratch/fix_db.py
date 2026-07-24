import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dotenv
dotenv.load_dotenv()
from backend.database.session import engine
from sqlalchemy import text

try:
    from backend.database.base import Base
    # import all models to ensure metadata is populated
    from backend.models import __all__ as model_names
    
    with engine.connect() as conn:
        tables = Base.metadata.tables.keys()
        print(f"Applying schema updates to {len(tables)} tables...")
        
        for table_name in tables:
            queries = [
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;",
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS created_by VARCHAR;",
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS updated_by VARCHAR;"
            ]
            
            for q in queries:
                try:
                    conn.execute(text(q))
                except Exception as e:
                    pass # Ignore if table doesn't exist in DB yet or syntax fails
                    
        conn.commit()
        print("Successfully updated ALL database tables!")
except Exception as e:
    print(f"Failed to update database: {e}")
