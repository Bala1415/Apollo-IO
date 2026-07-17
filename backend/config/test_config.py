from backend.config import get_settings

def test_config():
    settings = get_settings()
    print("App Name:", settings.app.name)
    print("Environment:", settings.app.environment)
    print("Database URL:", settings.db.url)
    print("JWT Secret:", settings.security.jwt_secret)
    print("CORS Origins:", settings.security.allowed_origins)

if __name__ == "__main__":
    test_config()
