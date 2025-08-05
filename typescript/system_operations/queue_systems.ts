interface PrintJob {
    id: number;
    document: string;
    pages: number;
    priority: number;
    userId: string;
    timestamp: Date;
}

class PrintQueue {
    private jobs: PrintJob[] = [];

    addJob(job: Omit<PrintJob, 'timestamp'>): void {
        const newJob: PrintJob = { ...job, timestamp: new Date() };
        
        // Insert based on priority (higher priority first)
        let inserted = false;
        for (let i = 0; i < this.jobs.length; i++) {
            if (newJob.priority > this.jobs[i].priority) {
                this.jobs.splice(i, 0, newJob);
                inserted = true;
                break;
            }
        }
        
        if (!inserted) {
            this.jobs.push(newJob);
        }
        
        console.log(`Added print job: ${job.document} (Priority: ${job.priority})`);
    }

    processNext(): PrintJob | null {
        const job = this.jobs.shift();
        return job || null;
    }

    getStatus(): void {
        console.log(`Print Queue Status - ${this.jobs.length} jobs pending:`);
        this.jobs.forEach((job, index) => {
            console.log(`  ${index + 1}. ${job.document} (${job.pages} pages, Priority: ${job.priority}) - User: ${job.userId}`);
        });
    }

    getQueueLength(): number {
        return this.jobs.length;
    }

    cancelJob(jobId: number): boolean {
        const index = this.jobs.findIndex(job => job.id === jobId);
        if (index !== -1) {
            const canceledJob = this.jobs.splice(index, 1)[0];
            console.log(`Canceled job: ${canceledJob.document}`);
            return true;
        }
        return false;
    }
}

interface Task {
    id: number;
    name: string;
    priority: number;
    duration: number; // in milliseconds
    createdAt: Date;
    dependencies?: number[];
}

class CPUScheduler {
    private readyQueue: Task[] = [];
    private currentTask: Task | null = null;
    private completedTasks: Task[] = [];
    private isRunning: boolean = false;

    addTask(task: Omit<Task, 'createdAt'>): void {
        const newTask: Task = { ...task, createdAt: new Date() };
        
        // Insert based on priority (higher priority first)
        let inserted = false;
        for (let i = 0; i < this.readyQueue.length; i++) {
            if (newTask.priority > this.readyQueue[i].priority) {
                this.readyQueue.splice(i, 0, newTask);
                inserted = true;
                break;
            }
        }
        
        if (!inserted) {
            this.readyQueue.push(newTask);
        }
        
        console.log(`Task added to scheduler: ${task.name} (Priority: ${task.priority}, Duration: ${task.duration}ms)`);
    }

    async runScheduler(): Promise<void> {
        if (this.isRunning) {
            console.log('Scheduler is already running');
            return;
        }
        
        this.isRunning = true;
        console.log('Starting CPU scheduler...');

        while (this.readyQueue.length > 0) {
            const task = this.readyQueue.shift()!;
            
            // Check dependencies
            if (task.dependencies) {
                const dependenciesMet = task.dependencies.every(depId => 
                    this.completedTasks.some(completed => completed.id === depId)
                );
                
                if (!dependenciesMet) {
                    console.log(`Task ${task.name} waiting for dependencies...`);
                    this.readyQueue.push(task); // Put back at end of queue
                    continue;
                }
            }
            
            this.currentTask = task;
            console.log(`Executing task: ${task.name} (Duration: ${task.duration}ms)`);
            
            await new Promise(resolve => setTimeout(resolve, task.duration));
            
            this.completedTasks.push(task);
            this.currentTask = null;
            console.log(`Task completed: ${task.name}`);
        }
        
        this.isRunning = false;
        console.log('All tasks completed');
    }

    getStatus(): void {
        console.log('CPU Scheduler Status:');
        console.log(`  Current: ${this.currentTask ? this.currentTask.name : 'idle'}`);
        console.log(`  Ready Queue (${this.readyQueue.length} tasks):`);
        
        this.readyQueue.forEach((task, index) => {
            console.log(`    ${index + 1}. ${task.name} (Priority: ${task.priority})`);
        });
        
        console.log(`  Completed: ${this.completedTasks.length} tasks`);
    }

    getAverageWaitTime(): number {
        if (this.completedTasks.length === 0) return 0;
        
        const totalWaitTime = this.completedTasks.reduce((sum, task) => {
            return sum + (new Date().getTime() - task.createdAt.getTime());
        }, 0);
        
        return totalWaitTime / this.completedTasks.length;
    }
}

interface WebPage {
    url: string;
    content: string;
    links: string[];
    depth: number;
    timestamp: Date;
}

class WebCrawler {
    private queue: Array<{ url: string; depth: number }> = [];
    private visited: Set<string> = new Set();
    private crawledData: WebPage[] = [];
    private maxDepth: number;
    private maxPages: number;

    constructor(maxDepth: number = 3, maxPages: number = 50) {
        this.maxDepth = maxDepth;
        this.maxPages = maxPages;
    }

    addUrl(url: string, depth: number = 0): void {
        if (this.visited.has(url) || depth > this.maxDepth || this.crawledData.length >= this.maxPages) {
            return;
        }
        
        this.queue.push({ url, depth });
        this.visited.add(url);
        console.log(`Added to crawl queue: ${url} (depth: ${depth})`);
    }

    private async simulateFetchPage(url: string): Promise<WebPage> {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Mock page data
        const mockPages: Record<string, Omit<WebPage, 'depth' | 'timestamp'>> = {
            'https://example.com': {
                url: 'https://example.com',
                content: 'Welcome to Example.com - Home page with latest news and updates',
                links: ['https://example.com/about', 'https://example.com/products', 'https://example.com/blog']
            },
            'https://example.com/about': {
                url: 'https://example.com/about',
                content: 'About us - Learn about our company history and mission',
                links: ['https://example.com/contact', 'https://example.com/team', 'https://example.com/careers']
            },
            'https://example.com/products': {
                url: 'https://example.com/products',
                content: 'Our products - Discover our wide range of innovative solutions',
                links: ['https://example.com/product/1', 'https://example.com/product/2', 'https://example.com/product/3']
            },
            'https://example.com/blog': {
                url: 'https://example.com/blog',
                content: 'Company blog - Latest articles and industry insights',
                links: ['https://example.com/blog/post-1', 'https://example.com/blog/post-2']
            },
            'https://example.com/contact': {
                url: 'https://example.com/contact',
                content: 'Contact us - Get in touch with our support team',
                links: []
            },
            'https://example.com/team': {
                url: 'https://example.com/team',
                content: 'Meet our team - Profiles of our talented employees',
                links: []
            },
            'https://example.com/product/1': {
                url: 'https://example.com/product/1',
                content: 'Product 1 - Advanced analytics platform for businesses',
                links: []
            },
            'https://example.com/product/2': {
                url: 'https://example.com/product/2',
                content: 'Product 2 - Cloud-based collaboration tools',
                links: []
            }
        };
        
        const mockPage = mockPages[url];
        if (mockPage) {
            return {
                ...mockPage,
                depth: 0, // Will be set by caller
                timestamp: new Date()
            };
        }
        
        return {
            url,
            content: 'Page not found or unable to fetch content',
            links: [],
            depth: 0,
            timestamp: new Date()
        };
    }

    async crawl(): Promise<void> {
        console.log('Starting web crawl...');
        
        const batchSize = 3; // Process multiple URLs concurrently
        
        while (this.queue.length > 0 && this.crawledData.length < this.maxPages) {
            const batch = this.queue.splice(0, Math.min(batchSize, this.queue.length));
            
            const fetchPromises = batch.map(async ({ url, depth }) => {
                console.log(`Crawling: ${url} (depth: ${depth})`);
                
                const page = await this.simulateFetchPage(url);
                page.depth = depth;
                
                this.crawledData.push(page);
                
                // Add found links to queue
                const validLinks = page.links.filter(link => 
                    !this.visited.has(link) && 
                    link.startsWith('https://example.com') // Stay within domain
                );
                
                for (const link of validLinks) {
                    this.addUrl(link, depth + 1);
                }
                
                console.log(`  Found ${page.links.length} links on ${url}`);
                return page;
            });
            
            await Promise.all(fetchPromises);
            
            // Small delay between batches
            await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        console.log('Web crawl completed');
    }

    getResults(): WebPage[] {
        console.log(`\nCrawl Results - ${this.crawledData.length} pages crawled:`);
        
        this.crawledData.forEach(page => {
            const contentPreview = page.content.length > 60 
                ? page.content.substring(0, 60) + '...' 
                : page.content;
                
            console.log(`  [Depth ${page.depth}] ${page.url}`);
            console.log(`    Content: ${contentPreview}`);
            console.log(`    Links found: ${page.links.length}`);
            console.log(`    Crawled at: ${page.timestamp.toLocaleTimeString()}`);
        });
        
        return this.crawledData;
    }

    getStatistics(): { totalPages: number; avgDepth: number; totalLinks: number } {
        const totalPages = this.crawledData.length;
        const avgDepth = totalPages > 0 
            ? this.crawledData.reduce((sum, page) => sum + page.depth, 0) / totalPages 
            : 0;
        const totalLinks = this.crawledData.reduce((sum, page) => sum + page.links.length, 0);
        
        return { totalPages, avgDepth, totalLinks };
    }
}

async function demonstrateQueues(): Promise<void> {
    console.log('=== Print Spooling Queue Example ===');
    const printQueue = new PrintQueue();
    
    const jobs = [
        { id: 1, document: 'Resume.pdf', pages: 2, priority: 1, userId: 'alice' },
        { id: 2, document: 'Report.docx', pages: 10, priority: 3, userId: 'bob' },
        { id: 3, document: 'Invoice.pdf', pages: 1, priority: 2, userId: 'charlie' },
        { id: 4, document: 'Manual.pdf', pages: 50, priority: 1, userId: 'david' },
        { id: 5, document: 'Presentation.pptx', pages: 15, priority: 3, userId: 'eve' }
    ];
    
    jobs.forEach(job => printQueue.addJob(job));
    printQueue.getStatus();
    
    console.log('\nProcessing print jobs:');
    while (printQueue.getQueueLength() > 0) {
        const job = printQueue.processNext();
        if (job) {
            console.log(`Printing: ${job.document} (${job.pages} pages) for ${job.userId}`);
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }

    console.log('\n=== CPU Task Scheduling Example ===');
    const scheduler = new CPUScheduler();
    
    const tasks = [
        { id: 1, name: 'System Update', priority: 2, duration: 1000 },
        { id: 2, name: 'File Backup', priority: 1, duration: 2000 },
        { id: 3, name: 'Virus Scan', priority: 3, duration: 1500 },
        { id: 4, name: 'Email Sync', priority: 2, duration: 800, dependencies: [1] },
        { id: 5, name: 'Database Cleanup', priority: 1, duration: 1200 }
    ];
    
    tasks.forEach(task => scheduler.addTask(task));
    scheduler.getStatus();
    
    console.log('\nStarting task execution:');
    await scheduler.runScheduler();
    
    scheduler.getStatus();
    console.log(`Average wait time: ${scheduler.getAverageWaitTime().toFixed(2)}ms`);

    console.log('\n=== Web Crawler BFS Example ===');
    const crawler = new WebCrawler(2, 15);
    
    crawler.addUrl('https://example.com', 0);
    await crawler.crawl();
    
    const results = crawler.getResults();
    const stats = crawler.getStatistics();
    
    console.log('\nCrawl Statistics:');
    console.log(`  Total pages: ${stats.totalPages}`);
    console.log(`  Average depth: ${stats.avgDepth.toFixed(1)}`);
    console.log(`  Total links found: ${stats.totalLinks}`);
}

if (require.main === module) {
    demonstrateQueues().catch(console.error);
}

export { PrintQueue, CPUScheduler, WebCrawler };