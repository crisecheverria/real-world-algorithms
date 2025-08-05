import hashlib
import time
import threading
from typing import Any, Dict, List, Optional
from collections import OrderedDict
import secrets

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            
            # Check expiration
            if item.get('expiration') and time.time() > item['expiration']:
                del self.cache[key]
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return item['value']

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.capacity:
                # Remove least recently used item
                self.cache.popitem(last=False)
            
            expiration = None
            if ttl_seconds:
                expiration = time.time() + ttl_seconds
            
            self.cache[key] = {
                'value': value,
                'expiration': expiration
            }

    def size(self) -> int:
        return len(self.cache)

class DatabaseIndex:
    def __init__(self):
        self.index: Dict[str, List[int]] = {}
        self.lock = threading.RLock()

    def add_record(self, record_id: int, field: str, value: str) -> None:
        with self.lock:
            key = f"{field}:{value}"
            if key not in self.index:
                self.index[key] = []
            self.index[key].append(record_id)

    def find_records(self, field: str, value: str) -> List[int]:
        with self.lock:
            key = f"{field}:{value}"
            return self.index.get(key, []).copy()

    def create_composite_index(self, record_id: int, fields: Dict[str, str]) -> None:
        for field, value in fields.items():
            self.add_record(record_id, field, value)

    def get_index_stats(self) -> Dict[str, int]:
        with self.lock:
            return {
                'total_keys': len(self.index),
                'total_records': sum(len(records) for records in self.index.values())
            }

class PasswordManager:
    def __init__(self, salt_length: int = 32):
        self.passwords: Dict[str, str] = {}
        self.salt_length = salt_length
        self.lock = threading.RLock()

    def _generate_salt(self) -> str:
        return secrets.token_hex(self.salt_length)

    def _hash_password(self, password: str, salt: str) -> str:
        # Using PBKDF2 with SHA-256
        key = hashlib.pbkdf2_hmac('sha256', 
                                password.encode('utf-8'), 
                                salt.encode('utf-8'), 
                                100000)  # 100,000 iterations
        return key.hex()

    def store_password(self, username: str, password: str) -> None:
        with self.lock:
            salt = self._generate_salt()
            hashed_password = self._hash_password(password, salt)
            self.passwords[username] = f"{salt}:{hashed_password}"
            print(f"Password stored for user: {username}")

    def verify_password(self, username: str, password: str) -> bool:
        with self.lock:
            stored_data = self.passwords.get(username)
            if not stored_data:
                return False
            
            salt, hashed_password = stored_data.split(':', 1)
            input_hash = self._hash_password(password, salt)
            return input_hash == hashed_password

    def get_user_count(self) -> int:
        with self.lock:
            return len(self.passwords)

    def delete_user(self, username: str) -> bool:
        with self.lock:
            if username in self.passwords:
                del self.passwords[username]
                return True
            return False

def demonstrate_hash_tables():
    print("=== Redis-like Cache Example ===")
    cache = LRUCache(capacity=100)
    cache.set('user:123', 'John Doe', ttl_seconds=300)  # 5 minutes TTL
    cache.set('session:abc', 'active', ttl_seconds=1800)  # 30 minutes TTL
    cache.set('api:rate_limit:user123', {'requests': 100, 'reset_time': time.time() + 3600})
    
    user = cache.get('user:123')
    if user:
        print(f"Cached user: {user}")
    
    print(f"Cache size: {cache.size()}")

    print("\n=== Database Indexing Example ===")
    db_index = DatabaseIndex()
    db_index.add_record(1, 'email', 'john@example.com')
    db_index.add_record(2, 'email', 'jane@example.com')
    db_index.add_record(3, 'city', 'New York')
    db_index.add_record(4, 'city', 'New York')
    db_index.add_record(5, 'department', 'Engineering')
    
    # Composite indexing
    db_index.create_composite_index(6, {
        'email': 'alice@example.com',
        'city': 'San Francisco',
        'department': 'Engineering'
    })
    
    records = db_index.find_records('city', 'New York')
    print(f"Records in New York: {records}")
    
    engineering_records = db_index.find_records('department', 'Engineering')
    print(f"Engineering department records: {engineering_records}")
    
    stats = db_index.get_index_stats()
    print(f"Index stats: {stats}")

    print("\n=== Password Storage Example ===")
    pm = PasswordManager()
    pm.store_password('alice', 'secret123')
    pm.store_password('bob', 'mypassword')
    pm.store_password('charlie', 'supersecure456')
    
    print(f"Alice login valid: {pm.verify_password('alice', 'secret123')}")
    print(f"Alice wrong password: {pm.verify_password('alice', 'wrong')}")
    print(f"Bob login valid: {pm.verify_password('bob', 'mypassword')}")
    print(f"Total users: {pm.get_user_count()}")
    
    # Demonstrate user deletion
    pm.delete_user('charlie')
    print(f"Users after deletion: {pm.get_user_count()}")

if __name__ == "__main__":
    demonstrate_hash_tables()