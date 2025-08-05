import * as crypto from 'crypto';

interface CacheItem<T> {
    value: T;
    expiration?: number;
    accessTime: number;
}

class LRUCache<T> {
    private capacity: number;
    private cache: Map<string, CacheItem<T>>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.cache = new Map();
    }

    get(key: string): T | null {
        const item = this.cache.get(key);
        if (!item) return null;

        if (item.expiration && Date.now() > item.expiration) {
            this.cache.delete(key);
            return null;
        }

        item.accessTime = Date.now();
        this.cache.delete(key);
        this.cache.set(key, item);
        return item.value;
    }

    set(key: string, value: T, ttlMs?: number): void {
        if (this.cache.size >= this.capacity && !this.cache.has(key)) {
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
        }

        const expiration = ttlMs ? Date.now() + ttlMs : undefined;
        this.cache.set(key, {
            value,
            expiration,
            accessTime: Date.now()
        });
    }

    size(): number {
        return this.cache.size;
    }
}

class DatabaseIndex {
    private index: Map<string, number[]>;

    constructor() {
        this.index = new Map();
    }

    addRecord(id: number, field: string, value: string): void {
        const key = `${field}:${value}`;
        const records = this.index.get(key) || [];
        records.push(id);
        this.index.set(key, records);
    }

    findRecords(field: string, value: string): number[] {
        const key = `${field}:${value}`;
        return this.index.get(key) || [];
    }

    createCompositeIndex(id: number, fields: Record<string, string>): void {
        for (const [field, value] of Object.entries(fields)) {
            this.addRecord(id, field, value);
        }
    }
}

class PasswordManager {
    private passwords: Map<string, string>;
    private saltRounds: number;

    constructor(saltRounds: number = 10) {
        this.passwords = new Map();
        this.saltRounds = saltRounds;
    }

    private hashPassword(password: string, salt: string): string {
        return crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
    }

    private generateSalt(): string {
        return crypto.randomBytes(32).toString('hex');
    }

    storePassword(username: string, password: string): void {
        const salt = this.generateSalt();
        const hashedPassword = this.hashPassword(password, salt);
        this.passwords.set(username, `${salt}:${hashedPassword}`);
        console.log(`Password stored for user: ${username}`);
    }

    verifyPassword(username: string, password: string): boolean {
        const storedData = this.passwords.get(username);
        if (!storedData) return false;

        const [salt, hashedPassword] = storedData.split(':');
        const inputHash = this.hashPassword(password, salt);
        return inputHash === hashedPassword;
    }

    getUserCount(): number {
        return this.passwords.size;
    }
}

function demonstrateHashTables(): void {
    console.log('=== Redis-like Cache Example ===');
    const cache = new LRUCache<string>(100);
    cache.set('user:123', 'John Doe', 5 * 60 * 1000); // 5 minutes TTL
    cache.set('session:abc', 'active', 30 * 60 * 1000); // 30 minutes TTL
    
    const user = cache.get('user:123');
    if (user) {
        console.log(`Cached user: ${user}`);
    }

    console.log('\n=== Database Indexing Example ===');
    const dbIndex = new DatabaseIndex();
    dbIndex.addRecord(1, 'email', 'john@example.com');
    dbIndex.addRecord(2, 'email', 'jane@example.com');
    dbIndex.addRecord(3, 'city', 'New York');
    dbIndex.addRecord(4, 'city', 'New York');
    
    const records = dbIndex.findRecords('city', 'New York');
    console.log(`Records in New York: ${records}`);

    dbIndex.createCompositeIndex(5, {
        'email': 'alice@example.com',
        'city': 'San Francisco',
        'department': 'Engineering'
    });

    console.log('\n=== Password Storage Example ===');
    const pm = new PasswordManager();
    pm.storePassword('alice', 'secret123');
    pm.storePassword('bob', 'mypassword');
    
    console.log(`Alice login valid: ${pm.verifyPassword('alice', 'secret123')}`);
    console.log(`Alice wrong password: ${pm.verifyPassword('alice', 'wrong')}`);
    console.log(`Total users: ${pm.getUserCount()}`);
}

if (require.main === module) {
    demonstrateHashTables();
}

export { LRUCache, DatabaseIndex, PasswordManager };