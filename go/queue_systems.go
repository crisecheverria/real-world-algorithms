package main

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

type PrintJob struct {
	ID       int
	Document string
	Pages    int
	Priority int
	UserID   string
}

type PrintQueue struct {
	jobs []PrintJob
	mu   sync.Mutex
}

func NewPrintQueue() *PrintQueue {
	return &PrintQueue{
		jobs: make([]PrintJob, 0),
	}
}

func (pq *PrintQueue) AddJob(job PrintJob) {
	pq.mu.Lock()
	defer pq.mu.Unlock()
	
	inserted := false
	for i, existingJob := range pq.jobs {
		if job.Priority > existingJob.Priority {
			pq.jobs = append(pq.jobs[:i], append([]PrintJob{job}, pq.jobs[i:]...)...)
			inserted = true
			break
		}
	}
	
	if !inserted {
		pq.jobs = append(pq.jobs, job)
	}
	
	fmt.Printf("Added print job: %s (Priority: %d)\n", job.Document, job.Priority)
}

func (pq *PrintQueue) ProcessNext() *PrintJob {
	pq.mu.Lock()
	defer pq.mu.Unlock()
	
	if len(pq.jobs) == 0 {
		return nil
	}
	
	job := pq.jobs[0]
	pq.jobs = pq.jobs[1:]
	return &job
}

func (pq *PrintQueue) GetStatus() {
	pq.mu.Lock()
	defer pq.mu.Unlock()
	
	fmt.Printf("Print Queue Status - %d jobs pending:\n", len(pq.jobs))
	for i, job := range pq.jobs {
		fmt.Printf("  %d. %s (%d pages, Priority: %d) - User: %s\n", 
			i+1, job.Document, job.Pages, job.Priority, job.UserID)
	}
}

type Task struct {
	ID        int
	Name      string
	Priority  int
	Duration  time.Duration
	CreatedAt time.Time
}

type CPUScheduler struct {
	readyQueue   []Task
	currentTask  *Task
	completedTasks []Task
	mu           sync.RWMutex
	isRunning    bool
}

func NewCPUScheduler() *CPUScheduler {
	return &CPUScheduler{
		readyQueue:     make([]Task, 0),
		completedTasks: make([]Task, 0),
	}
}

func (cs *CPUScheduler) AddTask(task Task) {
	cs.mu.Lock()
	defer cs.mu.Unlock()
	
	task.CreatedAt = time.Now()
	
	inserted := false
	for i, existingTask := range cs.readyQueue {
		if task.Priority > existingTask.Priority {
			cs.readyQueue = append(cs.readyQueue[:i], append([]Task{task}, cs.readyQueue[i:]...)...)
			inserted = true
			break
		}
	}
	
	if !inserted {
		cs.readyQueue = append(cs.readyQueue, task)
	}
	
	fmt.Printf("Task added to scheduler: %s (Priority: %d, Duration: %v)\n", 
		task.Name, task.Priority, task.Duration)
}

func (cs *CPUScheduler) RunScheduler() {
	cs.mu.Lock()
	if cs.isRunning {
		cs.mu.Unlock()
		return
	}
	cs.isRunning = true
	cs.mu.Unlock()

	for {
		cs.mu.Lock()
		if len(cs.readyQueue) == 0 {
			cs.isRunning = false
			cs.mu.Unlock()
			break
		}
		
		task := cs.readyQueue[0]
		cs.readyQueue = cs.readyQueue[1:]
		cs.currentTask = &task
		cs.mu.Unlock()
		
		fmt.Printf("Executing task: %s (Duration: %v)\n", task.Name, task.Duration)
		time.Sleep(task.Duration)
		
		cs.mu.Lock()
		cs.completedTasks = append(cs.completedTasks, task)
		cs.currentTask = nil
		cs.mu.Unlock()
		
		fmt.Printf("Task completed: %s\n", task.Name)
	}
}

func (cs *CPUScheduler) GetStatus() {
	cs.mu.RLock()
	defer cs.mu.RUnlock()
	
	fmt.Printf("CPU Scheduler Status:\n")
	if cs.currentTask != nil {
		fmt.Printf("  Current: %s\n", cs.currentTask.Name)
	} else {
		fmt.Printf("  Current: idle\n")
	}
	
	fmt.Printf("  Ready Queue (%d tasks):\n", len(cs.readyQueue))
	for i, task := range cs.readyQueue {
		fmt.Printf("    %d. %s (Priority: %d)\n", i+1, task.Name, task.Priority)
	}
	
	fmt.Printf("  Completed: %d tasks\n", len(cs.completedTasks))
}

type WebPage struct {
	URL      string
	Content  string
	Links    []string
	Depth    int
	Visited  bool
}

type WebCrawler struct {
	queue       []WebPage
	visited     map[string]bool
	maxDepth    int
	mu          sync.RWMutex
	crawledData []WebPage
}

func NewWebCrawler(maxDepth int) *WebCrawler {
	return &WebCrawler{
		queue:       make([]WebPage, 0),
		visited:     make(map[string]bool),
		maxDepth:    maxDepth,
		crawledData: make([]WebPage, 0),
	}
}

func (wc *WebCrawler) AddURL(url string, depth int) {
	wc.mu.Lock()
	defer wc.mu.Unlock()
	
	if wc.visited[url] || depth > wc.maxDepth {
		return
	}
	
	page := WebPage{
		URL:     url,
		Depth:   depth,
		Visited: false,
	}
	
	wc.queue = append(wc.queue, page)
	wc.visited[url] = true
	fmt.Printf("Added to crawl queue: %s (depth: %d)\n", url, depth)
}

func (wc *WebCrawler) simulateFetchPage(url string) WebPage {
	time.Sleep(100 * time.Millisecond)
	
	mockPages := map[string]WebPage{
		"https://example.com": {
			URL:     "https://example.com",
			Content: "Welcome to Example.com - Home page content",
			Links:   []string{"https://example.com/about", "https://example.com/products"},
		},
		"https://example.com/about": {
			URL:     "https://example.com/about",
			Content: "About us page content",
			Links:   []string{"https://example.com/contact", "https://example.com/team"},
		},
		"https://example.com/products": {
			URL:     "https://example.com/products",
			Content: "Our products page content",
			Links:   []string{"https://example.com/product/1", "https://example.com/product/2"},
		},
		"https://example.com/contact": {
			URL:     "https://example.com/contact",
			Content: "Contact us page content",
			Links:   []string{},
		},
		"https://example.com/team": {
			URL:     "https://example.com/team",
			Content: "Meet our team page content",
			Links:   []string{},
		},
		"https://example.com/product/1": {
			URL:     "https://example.com/product/1",
			Content: "Product 1 details",
			Links:   []string{},
		},
		"https://example.com/product/2": {
			URL:     "https://example.com/product/2",
			Content: "Product 2 details",
			Links:   []string{},
		},
	}
	
	if page, exists := mockPages[url]; exists {
		return page
	}
	
	return WebPage{
		URL:     url,
		Content: "Page not found",
		Links:   []string{},
	}
}

func (wc *WebCrawler) Crawl() {
	for {
		wc.mu.Lock()
		if len(wc.queue) == 0 {
			wc.mu.Unlock()
			break
		}
		
		currentPage := wc.queue[0]
		wc.queue = wc.queue[1:]
		wc.mu.Unlock()
		
		fmt.Printf("Crawling: %s (depth: %d)\n", currentPage.URL, currentPage.Depth)
		
		fetchedPage := wc.simulateFetchPage(currentPage.URL)
		fetchedPage.Depth = currentPage.Depth
		fetchedPage.Visited = true
		
		wc.mu.Lock()
		wc.crawledData = append(wc.crawledData, fetchedPage)
		wc.mu.Unlock()
		
		for _, link := range fetchedPage.Links {
			wc.AddURL(link, currentPage.Depth+1)
		}
		
		fmt.Printf("  Found %d links on %s\n", len(fetchedPage.Links), currentPage.URL)
	}
}

func (wc *WebCrawler) GetResults() {
	wc.mu.RLock()
	defer wc.mu.RUnlock()
	
	fmt.Printf("\nCrawl Results - %d pages crawled:\n", len(wc.crawledData))
	for _, page := range wc.crawledData {
		contentPreview := page.Content
		if len(contentPreview) > 50 {
			contentPreview = contentPreview[:50] + "..."
		}
		fmt.Printf("  [Depth %d] %s\n", page.Depth, page.URL)
		fmt.Printf("    Content: %s\n", contentPreview)
		fmt.Printf("    Links found: %d\n", len(page.Links))
	}
}

func demonstrateQueues() {
	fmt.Println("=== Print Spooling Queue Example ===")
	printQueue := NewPrintQueue()
	
	jobs := []PrintJob{
		{1, "Resume.pdf", 2, 1, "alice"},
		{2, "Report.docx", 10, 3, "bob"},
		{3, "Invoice.pdf", 1, 2, "charlie"},
		{4, "Manual.pdf", 50, 1, "david"},
		{5, "Presentation.pptx", 15, 3, "eve"},
	}
	
	for _, job := range jobs {
		printQueue.AddJob(job)
	}
	
	printQueue.GetStatus()
	
	fmt.Println("\nProcessing print jobs:")
	for {
		job := printQueue.ProcessNext()
		if job == nil {
			break
		}
		fmt.Printf("Printing: %s (%d pages) for %s\n", job.Document, job.Pages, job.UserID)
		time.Sleep(500 * time.Millisecond)
	}

	fmt.Println("\n=== CPU Task Scheduling Example ===")
	scheduler := NewCPUScheduler()
	
	tasks := []Task{
		{1, "System Update", 2, 1 * time.Second, time.Time{}},
		{2, "File Backup", 1, 2 * time.Second, time.Time{}},
		{3, "Virus Scan", 3, 1500 * time.Millisecond, time.Time{}},
		{4, "Email Sync", 2, 800 * time.Millisecond, time.Time{}},
		{5, "Database Cleanup", 1, 1200 * time.Millisecond, time.Time{}},
	}
	
	for _, task := range tasks {
		scheduler.AddTask(task)
	}
	
	scheduler.GetStatus()
	
	fmt.Println("\nStarting task execution:")
	scheduler.RunScheduler()
	
	scheduler.GetStatus()

	fmt.Println("\n=== Web Crawler BFS Example ===")
	crawler := NewWebCrawler(2)
	
	crawler.AddURL("https://example.com", 0)
	
	fmt.Println("Starting web crawl...")
	crawler.Crawl()
	
	crawler.GetResults()
}

func main() {
	demonstrateQueues()
}