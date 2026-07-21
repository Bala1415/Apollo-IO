import os

def update_requirements():
    req_file = r"c:\Users\Balavignesh\Desktop\Apollo IO\requirements.txt"
    
    # Standard backend dependencies
    missing_deps = [
        "fastapi==0.115.0",
        "uvicorn==0.30.6",
        "sqlalchemy==2.0.35",
        "psycopg2-binary==2.9.12",
        "alembic==1.13.3",
        "pydantic==2.13.4",
        "pydantic-settings==2.8.1",
        "python-jose[cryptography]==3.5.0",
        "passlib[bcrypt]==1.7.4",
        "prometheus_client==0.25.0",
        "redis==8.0.1",
        "backoff==2.2.1",
        "psutil==7.2.2",
        "python-multipart==0.0.32"
    ]
    
    try:
        with open(req_file, 'r', encoding='utf-16le') as f:
            existing = f.read()
    except Exception:
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                existing = f.read()
        except:
            existing = ""
            
    to_add = []
    for dep in missing_deps:
        pkg_name = dep.split('==')[0].split('[')[0]
        if pkg_name.lower() not in existing.lower():
            to_add.append(dep)
            
    if to_add:
        # Determine encoding by checking the file again
        encoding = 'utf-16le'
        try:
            with open(req_file, 'r', encoding='utf-16le') as f:
                f.read()
        except:
            encoding = 'utf-8'
            
        with open(req_file, 'a', encoding=encoding) as f:
            if not existing.endswith('\n'):
                f.write('\n')
            for dep in to_add:
                f.write(dep + '\n')
        print(f"Added {len(to_add)} dependencies to requirements.txt")

if __name__ == "__main__":
    update_requirements()
