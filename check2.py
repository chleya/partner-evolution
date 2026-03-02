from src.core.storage import get_storage_manager

s = get_storage_manager()
beliefs = s.get_beliefs()
print(f"Total beliefs: {len(beliefs)}")

for i, b in enumerate(beliefs):
    content = b.get("content", "")[:50]
    conf = b.get("confidence")
    print(f"{i+1}. {content}... (conf: {conf})")
