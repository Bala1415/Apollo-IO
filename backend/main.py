import uvicorn
from dotenv import load_dotenv

load_dotenv()
from backend.core.factory import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
