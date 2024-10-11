import sys
import os

print("Current working directory:", os.getcwd())
project_root = os.path.dirname(os.path.abspath(__file__))
print("Project root:", project_root)
sys.path.insert(0, project_root)
print("Updated sys.path:", sys.path)

try:
    from app.endpoints import gmail_webhook
    print("Successfully imported gmail_webhook")
except ImportError as e:
    print(f"Failed to import gmail_webhook: {e}")

try:
    from app import main
    print("Successfully imported main")
except ImportError as e:
    print(f"Failed to import main: {e}")