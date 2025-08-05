interface Page {
    url: string;
    title: string;
    timestamp: Date;
}

class BrowserHistory {
    private backStack: Page[] = [];
    private forwardStack: Page[] = [];
    private currentPage: Page | null = null;

    visitPage(url: string, title: string): void {
        if (this.currentPage) {
            this.backStack.push(this.currentPage);
        }

        const newPage: Page = {
            url,
            title,
            timestamp: new Date()
        };

        this.currentPage = newPage;
        this.forwardStack = []; // Clear forward history when visiting new page

        console.log(`Visited: ${title} (${url})`);
    }

    goBack(): boolean {
        if (this.backStack.length === 0) {
            console.log('Cannot go back - no pages in history');
            return false;
        }

        if (this.currentPage) {
            this.forwardStack.push(this.currentPage);
        }

        const previousPage = this.backStack.pop()!;
        this.currentPage = previousPage;

        console.log(`Went back to: ${previousPage.title} (${previousPage.url})`);
        return true;
    }

    goForward(): boolean {
        if (this.forwardStack.length === 0) {
            console.log('Cannot go forward - no pages in forward history');
            return false;
        }

        if (this.currentPage) {
            this.backStack.push(this.currentPage);
        }

        const nextPage = this.forwardStack.pop()!;
        this.currentPage = nextPage;

        console.log(`Went forward to: ${nextPage.title} (${nextPage.url})`);
        return true;
    }

    getCurrentPage(): Page | null {
        return this.currentPage;
    }

    canGoBack(): boolean {
        return this.backStack.length > 0;
    }

    canGoForward(): boolean {
        return this.forwardStack.length > 0;
    }

    getHistoryStatus(): void {
        console.log('Browser History Status:');
        console.log(`  Current: ${this.currentPage ? `${this.currentPage.title} (${this.currentPage.url})` : 'No page loaded'}`);
        console.log(`  Back stack: ${this.backStack.length} pages`);
        console.log(`  Forward stack: ${this.forwardStack.length} pages`);

        if (this.backStack.length > 0) {
            const recentPages = this.backStack.slice(-3);
            console.log(`  Recent back pages: ${recentPages.map(p => p.title).join(' -> ')}`);
        }
    }

    clearHistory(): void {
        this.backStack = [];
        this.forwardStack = [];
        console.log('Browser history cleared');
    }

    getBackHistory(): Page[] {
        return [...this.backStack];
    }

    getForwardHistory(): Page[] {
        return [...this.forwardStack];
    }
}

interface CallFrame {
    functionName: string;
    parameters: Record<string, any>;
    localVars: Record<string, any>;
    returnAddress: number;
    lineNumber: number;
}

class CallStack {
    private frames: CallFrame[] = [];

    pushFrame(funcName: string, params: Record<string, any> = {}, lineNum: number = 0): void {
        const frame: CallFrame = {
            functionName: funcName,
            parameters: { ...params },
            localVars: {},
            returnAddress: this.frames.length,
            lineNumber: lineNum
        };

        this.frames.push(frame);
        console.log(`Called: ${funcName}() at line ${lineNum}`);
    }

    popFrame(): CallFrame | null {
        if (this.frames.length === 0) {
            return null;
        }

        const frame = this.frames.pop()!;
        console.log(`Returned from: ${frame.functionName}()`);
        return frame;
    }

    getCurrentFrame(): CallFrame | null {
        if (this.frames.length === 0) {
            return null;
        }
        return this.frames[this.frames.length - 1];
    }

    setLocalVariable(name: string, value: any): void {
        const frame = this.getCurrentFrame();
        if (frame) {
            frame.localVars[name] = value;
        }
    }

    getLocalVariable(name: string): any {
        const frame = this.getCurrentFrame();
        return frame ? frame.localVars[name] : undefined;
    }

    printStackTrace(): void {
        console.log('Stack Trace:');
        for (let i = this.frames.length - 1; i >= 0; i--) {
            const frame = this.frames[i];
            console.log(`  at ${frame.functionName}() line ${frame.lineNumber}`);
            
            if (Object.keys(frame.parameters).length > 0) {
                console.log(`    Parameters:`, frame.parameters);
            }
            if (Object.keys(frame.localVars).length > 0) {
                console.log(`    Local vars:`, frame.localVars);
            }
        }
    }

    getStackDepth(): number {
        return this.frames.length;
    }

    hasFrame(functionName: string): boolean {
        return this.frames.some(frame => frame.functionName === functionName);
    }

    getFrameByFunction(functionName: string): CallFrame | null {
        for (let i = this.frames.length - 1; i >= 0; i--) {
            if (this.frames[i].functionName === functionName) {
                return this.frames[i];
            }
        }
        return null;
    }
}

interface Action {
    type: string;
    description: string;
    data: any;
    timestamp: Date;
    undoData?: any;
}

class UndoRedoSystem<T = any> {
    private undoStack: Action[] = [];
    private redoStack: Action[] = [];
    private maxSize: number;

    constructor(maxSize: number = 50) {
        this.maxSize = maxSize;
    }

    executeAction(actionType: string, description: string, data: T, undoData?: T): void {
        const action: Action = {
            type: actionType,
            description,
            data,
            timestamp: new Date(),
            undoData
        };

        this.undoStack.push(action);

        // Maintain max size
        if (this.undoStack.length > this.maxSize) {
            this.undoStack.shift();
        }

        // Clear redo stack when new action is executed
        this.redoStack = [];

        console.log(`Executed: ${actionType} - ${description}`);
    }

    undo(): Action | null {
        if (this.undoStack.length === 0) {
            console.log('Nothing to undo');
            return null;
        }

        const action = this.undoStack.pop()!;
        this.redoStack.push(action);

        console.log(`Undid: ${action.type} - ${action.description}`);
        return action;
    }

    redo(): Action | null {
        if (this.redoStack.length === 0) {
            console.log('Nothing to redo');
            return null;
        }

        const action = this.redoStack.pop()!;
        this.undoStack.push(action);

        console.log(`Redid: ${action.type} - ${action.description}`);
        return action;
    }

    getHistory(): void {
        console.log('Undo/Redo System Status:');
        console.log(`  Undo stack: ${this.undoStack.length} actions`);
        console.log(`  Redo stack: ${this.redoStack.length} actions`);

        if (this.undoStack.length > 0) {
            console.log('  Recent actions (newest first):');
            const recentActions = this.undoStack.slice(-5).reverse();
            recentActions.forEach((action, index) => {
                const timeStr = action.timestamp.toLocaleTimeString();
                console.log(`    ${index + 1}. ${action.type}: ${action.description} (${timeStr})`);
            });
        }
    }

    canUndo(): boolean {
        return this.undoStack.length > 0;
    }

    canRedo(): boolean {
        return this.redoStack.length > 0;
    }

    clearHistory(): void {
        this.undoStack = [];
        this.redoStack = [];
        console.log('Cleared all undo/redo history');
    }

    getUndoActions(): Action[] {
        return [...this.undoStack];
    }

    getRedoActions(): Action[] {
        return [...this.redoStack];
    }

    peek(): Action | null {
        return this.undoStack.length > 0 ? this.undoStack[this.undoStack.length - 1] : null;
    }

    getActionCount(): number {
        return this.undoStack.length + this.redoStack.length;
    }
}

// Text Editor simulation using Undo/Redo
interface TextOperation {
    type: 'INSERT' | 'DELETE' | 'REPLACE';
    position: number;
    text?: string;
    deletedText?: string;
    length?: number;
}

class TextEditor {
    private content: string = '';
    private undoRedoSystem: UndoRedoSystem<TextOperation>;
    private selectionStart: number = 0;
    private selectionEnd: number = 0;

    constructor() {
        this.undoRedoSystem = new UndoRedoSystem<TextOperation>(100);
    }

    insert(text: string, position?: number): void {
        const pos = position ?? this.selectionStart;
        const operation: TextOperation = {
            type: 'INSERT',
            position: pos,
            text: text
        };

        this.content = this.content.slice(0, pos) + text + this.content.slice(pos);
        this.selectionStart = pos + text.length;
        this.selectionEnd = this.selectionStart;

        this.undoRedoSystem.executeAction(
            'INSERT',
            `Insert '${text}' at position ${pos}`,
            operation
        );
    }

    delete(position: number, length: number): void {
        const deletedText = this.content.slice(position, position + length);
        const operation: TextOperation = {
            type: 'DELETE',
            position: position,
            length: length,
            deletedText: deletedText
        };

        this.content = this.content.slice(0, position) + this.content.slice(position + length);
        this.selectionStart = position;
        this.selectionEnd = position;

        this.undoRedoSystem.executeAction(
            'DELETE',
            `Delete '${deletedText}' at position ${position}`,
            operation
        );
    }

    undo(): void {
        const action = this.undoRedoSystem.undo();
        if (action && action.data) {
            this.applyReverseOperation(action.data as TextOperation);
        }
    }

    redo(): void {
        const action = this.undoRedoSystem.redo();
        if (action && action.data) {
            this.applyOperation(action.data as TextOperation);
        }
    }

    private applyOperation(operation: TextOperation): void {
        switch (operation.type) {
            case 'INSERT':
                if (operation.text) {
                    this.content = this.content.slice(0, operation.position) + 
                                 operation.text + 
                                 this.content.slice(operation.position);
                }
                break;
            case 'DELETE':
                if (operation.length) {
                    this.content = this.content.slice(0, operation.position) + 
                                 this.content.slice(operation.position + operation.length);
                }
                break;
        }
    }

    private applyReverseOperation(operation: TextOperation): void {
        switch (operation.type) {
            case 'INSERT':
                if (operation.text) {
                    this.content = this.content.slice(0, operation.position) + 
                                 this.content.slice(operation.position + operation.text.length);
                }
                break;
            case 'DELETE':
                if (operation.deletedText) {
                    this.content = this.content.slice(0, operation.position) + 
                                 operation.deletedText + 
                                 this.content.slice(operation.position);
                }
                break;
        }
    }

    getContent(): string {
        return this.content;
    }

    getUndoRedoStatus(): void {
        this.undoRedoSystem.getHistory();
    }

    canUndo(): boolean {
        return this.undoRedoSystem.canUndo();
    }

    canRedo(): boolean {
        return this.undoRedoSystem.canRedo();
    }
}

// Function call simulation
function simulateRecursiveFunction(callStack: CallStack, n: number, depth: number = 0): number {
    callStack.pushFrame('factorial', { n }, 100 + depth);
    
    const currentFrame = callStack.getCurrentFrame();
    if (currentFrame) {
        currentFrame.localVars.depth = depth;
    }

    let result: number;
    if (n <= 1) {
        callStack.setLocalVariable('result', 1);
        result = 1;
    } else {
        callStack.setLocalVariable('temp', n - 1);
        const temp = simulateRecursiveFunction(callStack, n - 1, depth + 1);
        result = n * temp;
        callStack.setLocalVariable('result', result);
    }

    callStack.popFrame();
    return result;
}

function demonstrateStacks(): void {
    console.log('=== Browser Navigation History Example ===');
    const browser = new BrowserHistory();

    browser.visitPage('https://google.com', 'Google');
    browser.visitPage('https://github.com', 'GitHub');
    browser.visitPage('https://stackoverflow.com', 'Stack Overflow');
    browser.visitPage('https://reddit.com', 'Reddit');
    browser.visitPage('https://typescript.org', 'TypeScript');

    browser.getHistoryStatus();

    console.log('\nNavigating back and forward:');
    browser.goBack();
    browser.goBack();
    browser.getHistoryStatus();

    browser.goForward();
    browser.visitPage('https://news.ycombinator.com', 'Hacker News');
    browser.getHistoryStatus();

    console.log(`\nCan go back: ${browser.canGoBack()}, Can go forward: ${browser.canGoForward()}`);

    console.log('\n=== Function Call Stack Example ===');
    const callStack = new CallStack();

    console.log('Simulating recursive factorial calculation:');
    const result = simulateRecursiveFunction(callStack, 5);
    console.log(`Final result: ${result}`);

    console.log('\nSimulating nested function calls:');
    const nestedCallStack = new CallStack();
    nestedCallStack.pushFrame('main', {}, 1);
    nestedCallStack.setLocalVariable('user', 'Alice');

    nestedCallStack.pushFrame('processUser', { userId: 123 }, 15);
    nestedCallStack.setLocalVariable('userData', { name: 'Alice', role: 'admin' });

    nestedCallStack.pushFrame('validatePermissions', { role: 'admin' }, 45);
    nestedCallStack.setLocalVariable('hasAccess', true);

    nestedCallStack.pushFrame('checkDatabase', { query: 'SELECT * FROM permissions' }, 67);
    nestedCallStack.setLocalVariable('dbResult', { permissions: ['read', 'write', 'admin'] });

    nestedCallStack.printStackTrace();

    console.log('\nUnwinding the stack:');
    while (nestedCallStack.getStackDepth() > 0) {
        nestedCallStack.popFrame();
    }

    console.log('\n=== Text Editor Undo/Redo Example ===');
    const editor = new TextEditor();

    console.log('Simulating text editing operations:');
    editor.insert('Hello');
    console.log(`Content: "${editor.getContent()}"`);

    editor.insert(' World');
    console.log(`Content: "${editor.getContent()}"`);

    editor.insert('!', 11);
    console.log(`Content: "${editor.getContent()}"`);

    editor.delete(5, 6); // Delete " World"
    console.log(`Content: "${editor.getContent()}"`);

    editor.insert(' TypeScript');
    console.log(`Content: "${editor.getContent()}"`);

    editor.getUndoRedoStatus();

    console.log('\nUndo operations:');
    editor.undo();
    console.log(`Content after undo: "${editor.getContent()}"`);
    
    editor.undo();
    console.log(`Content after undo: "${editor.getContent()}"`);

    console.log('\nRedo operations:');
    editor.redo();
    console.log(`Content after redo: "${editor.getContent()}"`);

    editor.getUndoRedoStatus();

    console.log('\n=== Advanced Undo/Redo System Example ===');
    const undoSystem = new UndoRedoSystem<any>(10);

    // Simulate drawing application operations
    undoSystem.executeAction('DRAW_LINE', 'Draw line from (0,0) to (100,100)', 
        { start: [0, 0], end: [100, 100], color: 'black', thickness: 2 });
    
    undoSystem.executeAction('DRAW_CIRCLE', 'Draw circle at (50,50) radius 25', 
        { center: [50, 50], radius: 25, fill: 'blue' });
    
    undoSystem.executeAction('CHANGE_COLOR', 'Change line color to red', 
        { objectId: 1, newColor: 'red', oldColor: 'black' });
    
    undoSystem.executeAction('MOVE_OBJECT', 'Move circle to (75,75)', 
        { objectId: 2, newPosition: [75, 75], oldPosition: [50, 50] });

    undoSystem.getHistory();

    console.log('\nUndo last two operations:');
    undoSystem.undo();
    undoSystem.undo();

    console.log('\nExecute new operation (clears redo stack):');
    undoSystem.executeAction('DRAW_RECTANGLE', 'Draw rectangle at (10,10)', 
        { position: [10, 10], size: [50, 30], fill: 'green' });

    undoSystem.getHistory();

    console.log(`\nSystem status - Can undo: ${undoSystem.canUndo()}, Can redo: ${undoSystem.canRedo()}`);
    console.log(`Total actions tracked: ${undoSystem.getActionCount()}`);
}

if (require.main === module) {
    demonstrateStacks();
}

export { BrowserHistory, CallStack, UndoRedoSystem, TextEditor };