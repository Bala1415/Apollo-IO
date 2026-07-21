import os
import glob
import re

models_dir = r"c:\Users\dhink\OneDrive\Desktop\Apollo-IO\backend\models"

for filepath in glob.glob(os.path.join(models_dir, "*.py")):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    
    # Replace dialect imports
    content = re.sub(r"from sqlalchemy\.dialects\.postgresql import (.*?)UUID(.*?)", r"from sqlalchemy.types import \1UUID\2", content)
    content = re.sub(r"from sqlalchemy\.dialects\.postgresql import (.*?)JSONB(.*?)", r"from sqlalchemy.types import \1JSON\2", content)
    # Sometimes they are on the same line: from sqlalchemy.dialects.postgresql import UUID, JSONB
    content = re.sub(r"from sqlalchemy\.dialects\.postgresql import .*UUID.*JSONB.*", r"from sqlalchemy.types import UUID, JSON", content)
    content = re.sub(r"from sqlalchemy\.dialects\.postgresql import .*JSONB.*UUID.*", r"from sqlalchemy.types import UUID, JSON", content)

    # Replace usages
    content = content.replace("JSONB", "JSON")

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")
