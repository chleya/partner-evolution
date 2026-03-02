import sys
sys.path.insert(0, r'F:\ai_partner_evolution')
from src.core.storage import get_storage_manager

storage = get_storage_manager()
beliefs = storage.get_beliefs()

# Print all belief contents
for i, b in enumerate(beliefs):
    print(f"{i+1}. {b.get('content')}")
    print(f"   confidence: {b.get('confidence')}")
    print()
