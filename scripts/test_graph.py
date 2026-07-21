import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

try:
    from ai.graph.graph import compiled_graph
    print("Successfully imported compiled_graph!")
except Exception as e:
    print(f"Error importing graph: {e}")
