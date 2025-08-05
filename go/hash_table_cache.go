package main

import (
	"crypto/sha256"
	"fmt"
	"sync"
	"time"
)

type CacheItem struct {
	value      interface{}
	expiration int64
}

type LRUCache struct {
	capacity int
	cache    map[string]*CacheItem
	mutex    sync.RWMutex
}

func NewLRUCache(capacity int) *LRUCache {
	return &LRUCache{
		capacity: capacity,
		cache:    make(map[string]*CacheItem),
	}
}

func (c *LRUCache) Get(key string) (interface{}, bool) {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	
	item, exists := c.cache[key]
	if !exists {
		return nil, false
	}
	
	if item.expiration > 0 && time.Now().Unix() > item.expiration {
		delete(c.cache, key)
		return nil, false
	}
	
	return item.value, true
}

func (c *LRUCache) Set(key string, value interface{}, ttl time.Duration) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	expiration := int64(0)
	if ttl > 0 {
		expiration = time.Now().Add(ttl).Unix()
	}
	
	c.cache[key] = &CacheItem{
		value:      value,
		expiration: expiration,
	}
}

type DatabaseIndex struct {
	index map[string][]int
	mutex sync.RWMutex
}

func NewDatabaseIndex() *DatabaseIndex {
	return &DatabaseIndex{
		index: make(map[string][]int),
	}
}

func (db *DatabaseIndex) AddRecord(id int, field string, value string) {
	db.mutex.Lock()
	defer db.mutex.Unlock()
	
	key := fmt.Sprintf("%s:%s", field, value)
	db.index[key] = append(db.index[key], id)
}

func (db *DatabaseIndex) FindRecords(field string, value string) []int {
	db.mutex.RLock()
	defer db.mutex.RUnlock()
	
	key := fmt.Sprintf("%s:%s", field, value)
	return db.index[key]
}

type PasswordManager struct {
	passwords map[string]string
	mutex     sync.RWMutex
}

func NewPasswordManager() *PasswordManager {
	return &PasswordManager{
		passwords: make(map[string]string),
	}
}

func (pm *PasswordManager) hashPassword(password string) string {
	hash := sha256.Sum256([]byte(password))
	return fmt.Sprintf("%x", hash)
}

func (pm *PasswordManager) StorePassword(username, password string) {
	pm.mutex.Lock()
	defer pm.mutex.Unlock()
	
	hashedPassword := pm.hashPassword(password)
	pm.passwords[username] = hashedPassword
	fmt.Printf("Password stored for user: %s\n", username)
}

func (pm *PasswordManager) VerifyPassword(username, password string) bool {
	pm.mutex.RLock()
	defer pm.mutex.RUnlock()
	
	storedHash, exists := pm.passwords[username]
	if !exists {
		return false
	}
	
	return storedHash == pm.hashPassword(password)
}

func main() {
	fmt.Println("=== Redis-like Cache Example ===")
	cache := NewLRUCache(100)
	cache.Set("user:123", "John Doe", 5*time.Minute)
	cache.Set("session:abc", "active", 30*time.Minute)
	
	if value, found := cache.Get("user:123"); found {
		fmt.Printf("Cached user: %s\n", value)
	}

	fmt.Println("\n=== Database Indexing Example ===")
	dbIndex := NewDatabaseIndex()
	dbIndex.AddRecord(1, "email", "john@example.com")
	dbIndex.AddRecord(2, "email", "jane@example.com")
	dbIndex.AddRecord(3, "city", "New York")
	dbIndex.AddRecord(4, "city", "New York")
	
	records := dbIndex.FindRecords("city", "New York")
	fmt.Printf("Records in New York: %v\n", records)

	fmt.Println("\n=== Password Storage Example ===")
	pm := NewPasswordManager()
	pm.StorePassword("alice", "secret123")
	pm.StorePassword("bob", "mypassword")
	
	fmt.Printf("Alice login valid: %t\n", pm.VerifyPassword("alice", "secret123"))
	fmt.Printf("Alice wrong password: %t\n", pm.VerifyPassword("alice", "wrong"))
}