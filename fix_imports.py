import os
import re

def fix_imports_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to match: `from models...` -> `from backend.models...`
    # and `from database...` -> `from backend.database...`
    # and `from repositories...` -> `from backend.repositories...`
    
    # regex pattern
    pattern = r'^(from|import)\s+(api|core|models|services|repositories|schemas|database|config|workers|utils|security)'
    
    def repl(m):
        return f"{m.group(1)} backend.{m.group(2)}"
        
    new_content = re.sub(pattern, repl, content, flags=re.MULTILINE)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

def main():
    backend_dir = r"c:\Users\Balavignesh\Desktop\Apollo IO\backend"
    for root, dirs, files in os.walk(backend_dir):
        if 'venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                fix_imports_in_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
