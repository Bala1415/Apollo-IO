import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dotenv
dotenv.load_dotenv()
from backend.database.session import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        db_name = conn.scalar(text('SELECT current_database()'))
        print(f"Connected to Database: {db_name}\n")
        
        # Query the raw_leads table
        result = conn.execute(text("SELECT email, company_domain, status, created_at FROM raw_leads")).fetchall()
        
        if not result:
            print("The raw_leads table is currently empty. Try syncing from the extension first!")
        else:
            print(f"Found {len(result)} leads in the database:")
            print("-" * 60)
            for row in result:
                print(f"Email: {row[0]}")
                print(f"Company: {row[1]}")
                print(f"Status: {row[2]}")
                print(f"Created At: {row[3]}")
                print("-" * 60)
                
except Exception as e:
    print(f"Failed to connect or read database: {e}")
