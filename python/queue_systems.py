import asyncio
import time
from collections import deque
from datetime import datetime
from typing import List, Dict, Optional, Set
import heapq

class PrintJob:
    def __init__(self, job_id: int, document: str, pages: int, priority: int, user_id: str):
        self.id = job_id
        self.document = document
        self.pages = pages
        self.priority = priority
        self.user_id = user_id
        self.timestamp = datetime.now()
    
    def __lt__(self, other):
        # Higher priority jobs come first (reverse order for heapq)
        return self.priority > other.priority

class PrintQueue:
    def __init__(self):
        self.jobs = []  # Using heapq for priority queue
        self.job_counter = 0
    
    def add_job(self, job: PrintJob) -> None:
        # Use counter to maintain insertion order for equal priorities
        heapq.heappush(self.jobs, (job, self.job_counter))
        self.job_counter += 1
        print(f"Added print job: {job.document} (Priority: {job.priority})")
    
    def process_next(self) -> Optional[PrintJob]:
        if not self.jobs:
            return None
        
        job, _ = heapq.heappop(self.jobs)
        return job
    
    def get_status(self) -> None:
        print(f"Print Queue Status - {len(self.jobs)} jobs pending:")
        # Sort jobs by priority for display (without modifying the heap)
        sorted_jobs = sorted([job for job, _ in self.jobs], key=lambda x: (-x.priority, x.timestamp))
        
        for i, job in enumerate(sorted_jobs, 1):
            print(f"  {i}. {job.document} ({job.pages} pages, Priority: {job.priority}) - User: {job.user_id}")
    
    def cancel_job(self, job_id: int) -> bool:
        """Cancel a job by ID"""
        for i, (job, counter) in enumerate(self.jobs):
            if job.id == job_id:
                print(f"Canceled job: {job.document}")
                self.jobs[i] = (self.jobs[-1][0], self.jobs[-1][1])  # Replace with last element
                self.jobs.pop()
                heapq.heapify(self.jobs)  # Rebuild heap
                return True
        return False
    
    def get_estimated_wait_time(self, target_job_id: int) -> int:
        """Estimate wait time for a specific job in minutes"""
        wait_time = 0
        for job, _ in sorted(self.jobs, key=lambda x: (-x[0].priority, x[0].timestamp)):
            if job.id == target_job_id:
                break
            wait_time += job.pages * 0.5  # Assume 30 seconds per page
        return int(wait_time)

class Task:
    def __init__(self, task_id: int, name: str, priority: int, duration: float, dependencies: List[int] = None):
        self.id = task_id
        self.name = name
        self.priority = priority
        self.duration = duration  # in seconds
        self.dependencies = dependencies or []
        self.created_at = datetime.now()
    
    def __lt__(self, other):
        return self.priority > other.priority

class CPUScheduler:
    def __init__(self):
        self.ready_queue = []  # Priority queue
        self.current_task: Optional[Task] = None
        self.completed_tasks: List[Task] = []
        self.waiting_tasks: List[Task] = []  # Tasks waiting for dependencies
        self.is_running = False
        self.task_counter = 0
    
    def add_task(self, task: Task) -> None:
        if self._dependencies_met(task):
            heapq.heappush(self.ready_queue, (task, self.task_counter))
        else:
            self.waiting_tasks.append(task)
        
        self.task_counter += 1
        deps_str = f" (depends on: {task.dependencies})" if task.dependencies else ""
        print(f"Task added to scheduler: {task.name} (Priority: {task.priority}, Duration: {task.duration}s){deps_str}")
    
    def _dependencies_met(self, task: Task) -> bool:
        if not task.dependencies:
            return True
        
        completed_ids = {t.id for t in self.completed_tasks}
        return all(dep_id in completed_ids for dep_id in task.dependencies)
    
    def _check_waiting_tasks(self) -> None:
        """Move tasks from waiting to ready queue if dependencies are met"""
        ready_tasks = []
        still_waiting = []
        
        for task in self.waiting_tasks:
            if self._dependencies_met(task):
                ready_tasks.append(task)
            else:
                still_waiting.append(task)
        
        for task in ready_tasks:
            heapq.heappush(self.ready_queue, (task, self.task_counter))
            self.task_counter += 1
            print(f"Task {task.name} moved to ready queue (dependencies met)")
        
        self.waiting_tasks = still_waiting
    
    async def run_scheduler(self) -> None:
        if self.is_running:
            print("Scheduler is already running")
            return
        
        self.is_running = True
        print("Starting CPU scheduler...")
        
        while self.ready_queue or self.waiting_tasks:
            self._check_waiting_tasks()
            
            if not self.ready_queue:
                if self.waiting_tasks:
                    print("All remaining tasks are waiting for dependencies...")
                    break
                else:
                    break
            
            task, _ = heapq.heappop(self.ready_queue)
            self.current_task = task
            
            print(f"Executing task: {task.name} (Duration: {task.duration}s)")
            start_time = time.time()
            
            await asyncio.sleep(task.duration)
            
            execution_time = time.time() - start_time
            print(f"Task completed: {task.name} (actual time: {execution_time:.2f}s)")
            
            self.completed_tasks.append(task)
            self.current_task = None
        
        self.is_running = False
        if self.waiting_tasks:
            print(f"Warning: {len(self.waiting_tasks)} tasks remain with unmet dependencies")
        print("All executable tasks completed")
    
    def get_status(self) -> None:
        print("CPU Scheduler Status:")
        print(f"  Current: {self.current_task.name if self.current_task else 'idle'}")
        
        ready_tasks = sorted([task for task, _ in self.ready_queue], key=lambda x: (-x.priority, x.created_at))
        print(f"  Ready Queue ({len(ready_tasks)} tasks):")
        for i, task in enumerate(ready_tasks, 1):
            print(f"    {i}. {task.name} (Priority: {task.priority})")
        
        if self.waiting_tasks:
            print(f"  Waiting for dependencies ({len(self.waiting_tasks)} tasks):")
            for i, task in enumerate(self.waiting_tasks, 1):
                print(f"    {i}. {task.name} (waiting for: {task.dependencies})")
        
        print(f"  Completed: {len(self.completed_tasks)} tasks")
    
    def get_average_wait_time(self) -> float:
        if not self.completed_tasks:
            return 0.0
        
        total_wait_time = sum(
            (datetime.now() - task.created_at).total_seconds() 
            for task in self.completed_tasks
        )
        return total_wait_time / len(self.completed_tasks)

class WebPage:
    def __init__(self, url: str, content: str = "", links: List[str] = None, depth: int = 0):
        self.url = url
        self.content = content
        self.links = links or []
        self.depth = depth
        self.timestamp = datetime.now()

class WebCrawler:
    def __init__(self, max_depth: int = 3, max_pages: int = 50, delay: float = 0.1):
        self.queue = deque()  # BFS queue
        self.visited: Set[str] = set()
        self.crawled_data: List[WebPage] = []
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay  # Delay between requests
        self.robots_txt_rules: Dict[str, List[str]] = {}
    
    def add_url(self, url: str, depth: int = 0) -> None:
        if (url in self.visited or 
            depth > self.max_depth or 
            len(self.crawled_data) >= self.max_pages):
            return
        
        self.queue.append((url, depth))
        self.visited.add(url)
        print(f"Added to crawl queue: {url} (depth: {depth})")
    
    async def _simulate_fetch_page(self, url: str) -> WebPage:
        """Simulate fetching a web page with realistic data"""
        await asyncio.sleep(self.delay)  # Simulate network delay
        
        # Mock page database
        mock_pages = {
            'https://example.com': WebPage(
                url='https://example.com',
                content='Welcome to Example.com - Your trusted source for innovative solutions and cutting-edge technology',
                links=['https://example.com/about', 'https://example.com/products', 'https://example.com/blog', 'https://example.com/contact']
            ),
            'https://example.com/about': WebPage(
                url='https://example.com/about',
                content='About Example.com - Founded in 2010, we are a leading technology company specializing in web solutions',
                links=['https://example.com/team', 'https://example.com/careers', 'https://example.com/history']
            ),
            'https://example.com/products': WebPage(
                url='https://example.com/products',
                content='Our Products - Discover our comprehensive suite of software solutions designed for modern businesses',
                links=['https://example.com/product/analytics', 'https://example.com/product/crm', 'https://example.com/product/api']
            ),
            'https://example.com/blog': WebPage(
                url='https://example.com/blog',
                content='Company Blog - Stay updated with the latest industry trends, insights, and company news',
                links=['https://example.com/blog/tech-trends-2024', 'https://example.com/blog/ai-revolution', 'https://example.com/blog/web-security']
            ),
            'https://example.com/contact': WebPage(
                url='https://example.com/contact',
                content='Contact Us - Get in touch with our expert team for support, sales, or partnership opportunities',
                links=['https://example.com/support', 'https://example.com/sales']
            ),
            'https://example.com/team': WebPage(
                url='https://example.com/team',
                content='Our Team - Meet the talented individuals behind our innovative products and services',
                links=[]
            ),
            'https://example.com/product/analytics': WebPage(
                url='https://example.com/product/analytics',
                content='Analytics Platform - Advanced data analytics and visualization tools for business intelligence',
                links=['https://example.com/product/analytics/features', 'https://example.com/product/analytics/pricing']
            ),
            'https://example.com/blog/tech-trends-2024': WebPage(
                url='https://example.com/blog/tech-trends-2024',
                content='Technology Trends 2024 - Exploring the most significant technological developments shaping the future',
                links=[]
            )
        }
        
        if url in mock_pages:
            page = mock_pages[url]
            # Filter links to stay within domain and respect depth
            valid_links = [link for link in page.links if link.startswith('https://example.com')]
            page.links = valid_links
            return page
        
        return WebPage(
            url=url,
            content='Page not found or unable to fetch content',
            links=[]
        )
    
    def _is_allowed_by_robots(self, url: str) -> bool:
        """Simulate robots.txt checking"""
        # In a real crawler, this would parse robots.txt
        disallowed_paths = ['/admin', '/private', '/internal']
        return not any(path in url for path in disallowed_paths)
    
    async def crawl(self, concurrent_requests: int = 3) -> None:
        print("Starting web crawl...")
        
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        while self.queue and len(self.crawled_data) < self.max_pages:
            # Process multiple URLs concurrently
            batch_size = min(concurrent_requests, len(self.queue))
            batch = []
            
            for _ in range(batch_size):
                if self.queue:
                    batch.append(self.queue.popleft())
            
            tasks = [self._crawl_single_page(url, depth, semaphore) for url, depth in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"Web crawl completed - {len(self.crawled_data)} pages crawled")
    
    async def _crawl_single_page(self, url: str, depth: int, semaphore: asyncio.Semaphore) -> None:
        async with semaphore:
            if not self._is_allowed_by_robots(url):
                print(f"Skipping {url} (blocked by robots.txt)")
                return
            
            print(f"Crawling: {url} (depth: {depth})")
            
            try:
                page = await self._simulate_fetch_page(url)
                page.depth = depth
                
                self.crawled_data.append(page)
                
                # Add discovered links to queue
                for link in page.links:
                    if link not in self.visited:
                        self.add_url(link, depth + 1)
                
                print(f"  Found {len(page.links)} links on {url}")
                
            except Exception as e:
                print(f"Error crawling {url}: {e}")
    
    def get_results(self) -> List[WebPage]:
        print(f"\nCrawl Results - {len(self.crawled_data)} pages crawled:")
        
        for page in self.crawled_data:
            content_preview = (page.content[:80] + '...') if len(page.content) > 80 else page.content
            print(f"  [Depth {page.depth}] {page.url}")
            print(f"    Content: {content_preview}")
            print(f"    Links found: {len(page.links)}")
            print(f"    Crawled at: {page.timestamp.strftime('%H:%M:%S')}")
        
        return self.crawled_data
    
    def get_statistics(self) -> Dict[str, float]:
        if not self.crawled_data:
            return {"total_pages": 0, "avg_depth": 0, "total_links": 0, "pages_per_depth": {}}
        
        total_pages = len(self.crawled_data)
        avg_depth = sum(page.depth for page in self.crawled_data) / total_pages
        total_links = sum(len(page.links) for page in self.crawled_data)
        
        # Pages per depth level
        depth_counts = {}
        for page in self.crawled_data:
            depth_counts[page.depth] = depth_counts.get(page.depth, 0) + 1
        
        return {
            "total_pages": total_pages,
            "avg_depth": round(avg_depth, 2),
            "total_links": total_links,
            "pages_per_depth": depth_counts,
            "avg_links_per_page": round(total_links / total_pages, 2)
        }
    
    def export_sitemap(self) -> List[str]:
        """Export discovered URLs as a sitemap"""
        return sorted([page.url for page in self.crawled_data])

async def demonstrate_queues():
    print("=== Print Spooling Queue Example ===")
    print_queue = PrintQueue()
    
    jobs = [
        PrintJob(1, "Resume.pdf", 2, 1, "alice"),
        PrintJob(2, "Report.docx", 10, 3, "bob"),
        PrintJob(3, "Invoice.pdf", 1, 2, "charlie"),
        PrintJob(4, "Manual.pdf", 50, 1, "david"),
        PrintJob(5, "Presentation.pptx", 15, 3, "eve"),
        PrintJob(6, "Urgent_Contract.pdf", 5, 4, "frank")  # Highest priority
    ]
    
    for job in jobs:
        print_queue.add_job(job)
    
    print_queue.get_status()
    
    print(f"\nEstimated wait time for job 4: {print_queue.get_estimated_wait_time(4)} minutes")
    
    print("\nProcessing print jobs:")
    while True:
        job = print_queue.process_next()
        if not job:
            break
        print(f"Printing: {job.document} ({job.pages} pages) for {job.user_id}")
        await asyncio.sleep(0.5)  # Simulate printing time

    print("\n=== CPU Task Scheduling Example ===")
    scheduler = CPUScheduler()
    
    tasks = [
        Task(1, "System Initialization", 3, 0.8),
        Task(2, "Load Configuration", 2, 0.5, dependencies=[1]),
        Task(3, "Start Database", 3, 1.2, dependencies=[1]),
        Task(4, "Start Web Server", 2, 0.7, dependencies=[2, 3]),
        Task(5, "Background Cleanup", 1, 1.5),
        Task(6, "Health Check", 2, 0.3, dependencies=[4]),
        Task(7, "Send Notifications", 1, 0.4, dependencies=[4])
    ]
    
    for task in tasks:
        scheduler.add_task(task)
    
    scheduler.get_status()
    
    print("\nStarting task execution:")
    await scheduler.run_scheduler()
    
    scheduler.get_status()
    print(f"Average wait time: {scheduler.get_average_wait_time():.2f} seconds")

    print("\n=== Web Crawler BFS Example ===")
    crawler = WebCrawler(max_depth=2, max_pages=15, delay=0.1)
    
    crawler.add_url('https://example.com', 0)
    await crawler.crawl(concurrent_requests=2)
    
    results = crawler.get_results()
    stats = crawler.get_statistics()
    
    print("\nCrawl Statistics:")
    for key, value in stats.items():
        if key != "pages_per_depth":
            print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print(f"  Pages per depth: {dict(value)}")
    
    print(f"\nSitemap ({len(crawler.export_sitemap())} URLs):")
    for url in crawler.export_sitemap()[:10]:  # Show first 10
        print(f"  {url}")

if __name__ == "__main__":
    asyncio.run(demonstrate_queues())