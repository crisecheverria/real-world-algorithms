package main

import (
	"fmt"
	"strings"
	"time"
)

type Page struct {
	URL       string
	Title     string
	Timestamp time.Time
}

type BrowserHistory struct {
	backStack    []Page
	forwardStack []Page
	currentPage  *Page
}

func NewBrowserHistory() *BrowserHistory {
	return &BrowserHistory{
		backStack:    make([]Page, 0),
		forwardStack: make([]Page, 0),
	}
}

func (bh *BrowserHistory) VisitPage(url, title string) {
	if bh.currentPage != nil {
		bh.backStack = append(bh.backStack, *bh.currentPage)
	}
	
	newPage := Page{
		URL:       url,
		Title:     title,
		Timestamp: time.Now(),
	}
	
	bh.currentPage = &newPage
	bh.forwardStack = make([]Page, 0)
	
	fmt.Printf("Visited: %s (%s)\n", title, url)
}

func (bh *BrowserHistory) GoBack() bool {
	if len(bh.backStack) == 0 {
		fmt.Println("Cannot go back - no pages in history")
		return false
	}
	
	if bh.currentPage != nil {
		bh.forwardStack = append(bh.forwardStack, *bh.currentPage)
	}
	
	lastIndex := len(bh.backStack) - 1
	previousPage := bh.backStack[lastIndex]
	bh.backStack = bh.backStack[:lastIndex]
	bh.currentPage = &previousPage
	
	fmt.Printf("Went back to: %s (%s)\n", previousPage.Title, previousPage.URL)
	return true
}

func (bh *BrowserHistory) GoForward() bool {
	if len(bh.forwardStack) == 0 {
		fmt.Println("Cannot go forward - no pages in forward history")
		return false
	}
	
	if bh.currentPage != nil {
		bh.backStack = append(bh.backStack, *bh.currentPage)
	}
	
	lastIndex := len(bh.forwardStack) - 1
	nextPage := bh.forwardStack[lastIndex]
	bh.forwardStack = bh.forwardStack[:lastIndex]
	bh.currentPage = &nextPage
	
	fmt.Printf("Went forward to: %s (%s)\n", nextPage.Title, nextPage.URL)
	return true
}

func (bh *BrowserHistory) GetCurrentPage() *Page {
	return bh.currentPage
}

func (bh *BrowserHistory) GetHistoryStatus() {
	fmt.Printf("Browser History Status:\n")
	if bh.currentPage != nil {
		fmt.Printf("  Current: %s (%s)\n", bh.currentPage.Title, bh.currentPage.URL)
	} else {
		fmt.Printf("  Current: No page loaded\n")
	}
	fmt.Printf("  Back stack: %d pages\n", len(bh.backStack))
	fmt.Printf("  Forward stack: %d pages\n", len(bh.forwardStack))
	
	if len(bh.backStack) > 0 {
		fmt.Printf("  Recent back pages: ")
		start := len(bh.backStack) - 3
		if start < 0 {
			start = 0
		}
		for i := start; i < len(bh.backStack); i++ {
			fmt.Printf("%s", bh.backStack[i].Title)
			if i < len(bh.backStack)-1 {
				fmt.Printf(" -> ")
			}
		}
		fmt.Println()
	}
}

type CallFrame struct {
	FunctionName string
	Parameters   map[string]interface{}
	LocalVars    map[string]interface{}
	ReturnAddr   int
	LineNumber   int
}

type CallStack struct {
	frames []CallFrame
}

func NewCallStack() *CallStack {
	return &CallStack{
		frames: make([]CallFrame, 0),
	}
}

func (cs *CallStack) PushFrame(funcName string, params map[string]interface{}, lineNum int) {
	frame := CallFrame{
		FunctionName: funcName,
		Parameters:   make(map[string]interface{}),
		LocalVars:    make(map[string]interface{}),
		ReturnAddr:   len(cs.frames),
		LineNumber:   lineNum,
	}
	
	for k, v := range params {
		frame.Parameters[k] = v
	}
	
	cs.frames = append(cs.frames, frame)
	fmt.Printf("Called: %s() at line %d\n", funcName, lineNum)
}

func (cs *CallStack) PopFrame() *CallFrame {
	if len(cs.frames) == 0 {
		return nil
	}
	
	lastIndex := len(cs.frames) - 1
	frame := cs.frames[lastIndex]
	cs.frames = cs.frames[:lastIndex]
	
	fmt.Printf("Returned from: %s()\n", frame.FunctionName)
	return &frame
}

func (cs *CallStack) GetCurrentFrame() *CallFrame {
	if len(cs.frames) == 0 {
		return nil
	}
	return &cs.frames[len(cs.frames)-1]
}

func (cs *CallStack) SetLocalVariable(name string, value interface{}) {
	if frame := cs.GetCurrentFrame(); frame != nil {
		frame.LocalVars[name] = value
	}
}

func (cs *CallStack) GetLocalVariable(name string) interface{} {
	if frame := cs.GetCurrentFrame(); frame != nil {
		return frame.LocalVars[name]
	}
	return nil
}

func (cs *CallStack) PrintStackTrace() {
	fmt.Println("Stack Trace:")
	for i := len(cs.frames) - 1; i >= 0; i-- {
		frame := cs.frames[i]
		fmt.Printf("  at %s() line %d\n", frame.FunctionName, frame.LineNumber)
		
		if len(frame.Parameters) > 0 {
			fmt.Printf("    Parameters: %v\n", frame.Parameters)
		}
		if len(frame.LocalVars) > 0 {
			fmt.Printf("    Local vars: %v\n", frame.LocalVars)
		}
	}
}

func (cs *CallStack) GetStackDepth() int {
	return len(cs.frames)
}

type Action struct {
	Type        string
	Description string
	Data        interface{}
	Timestamp   time.Time
}

type UndoRedoSystem struct {
	undoStack []Action
	redoStack []Action
	maxSize   int
}

func NewUndoRedoSystem(maxSize int) *UndoRedoSystem {
	return &UndoRedoSystem{
		undoStack: make([]Action, 0),
		redoStack: make([]Action, 0),
		maxSize:   maxSize,
	}
}

func (urs *UndoRedoSystem) ExecuteAction(actionType, description string, data interface{}) {
	action := Action{
		Type:        actionType,
		Description: description,
		Data:        data,
		Timestamp:   time.Now(),
	}
	
	urs.undoStack = append(urs.undoStack, action)
	
	if len(urs.undoStack) > urs.maxSize {
		urs.undoStack = urs.undoStack[1:]
	}
	
	urs.redoStack = make([]Action, 0)
	
	fmt.Printf("Executed: %s - %s\n", actionType, description)
}

func (urs *UndoRedoSystem) Undo() *Action {
	if len(urs.undoStack) == 0 {
		fmt.Println("Nothing to undo")
		return nil
	}
	
	lastIndex := len(urs.undoStack) - 1
	action := urs.undoStack[lastIndex]
	urs.undoStack = urs.undoStack[:lastIndex]
	
	urs.redoStack = append(urs.redoStack, action)
	
	fmt.Printf("Undid: %s - %s\n", action.Type, action.Description)
	return &action
}

func (urs *UndoRedoSystem) Redo() *Action {
	if len(urs.redoStack) == 0 {
		fmt.Println("Nothing to redo")
		return nil
	}
	
	lastIndex := len(urs.redoStack) - 1
	action := urs.redoStack[lastIndex]
	urs.redoStack = urs.redoStack[:lastIndex]
	
	urs.undoStack = append(urs.undoStack, action)
	
	fmt.Printf("Redid: %s - %s\n", action.Type, action.Description)
	return &action
}

func (urs *UndoRedoSystem) GetHistory() {
	fmt.Printf("Undo/Redo System Status:\n")
	fmt.Printf("  Undo stack: %d actions\n", len(urs.undoStack))
	fmt.Printf("  Redo stack: %d actions\n", len(urs.redoStack))
	
	if len(urs.undoStack) > 0 {
		fmt.Printf("  Recent actions (newest first):\n")
		start := len(urs.undoStack) - 5
		if start < 0 {
			start = 0
		}
		for i := len(urs.undoStack) - 1; i >= start; i-- {
			action := urs.undoStack[i]
			fmt.Printf("    %d. %s: %s (%s)\n", 
				len(urs.undoStack)-i, action.Type, action.Description, 
				action.Timestamp.Format("15:04:05"))
		}
	}
}

func (urs *UndoRedoSystem) CanUndo() bool {
	return len(urs.undoStack) > 0
}

func (urs *UndoRedoSystem) CanRedo() bool {
	return len(urs.redoStack) > 0
}

func (urs *UndoRedoSystem) ClearHistory() {
	urs.undoStack = make([]Action, 0)
	urs.redoStack = make([]Action, 0)
	fmt.Println("Cleared all undo/redo history")
}

func simulateRecursiveFunction(cs *CallStack, n int, depth int) int {
	cs.PushFrame("factorial", map[string]interface{}{"n": n}, 100+depth)
	
	if current := cs.GetCurrentFrame(); current != nil {
		current.LocalVars["depth"] = depth
	}
	
	var result int
	if n <= 1 {
		cs.SetLocalVariable("result", 1)
		result = 1
	} else {
		cs.SetLocalVariable("temp", n-1)
		temp := simulateRecursiveFunction(cs, n-1, depth+1)
		result = n * temp
		cs.SetLocalVariable("result", result)
	}
	
	cs.PopFrame()
	return result
}

func demonstrateStacks() {
	fmt.Println("=== Browser Navigation History Example ===")
	browser := NewBrowserHistory()
	
	browser.VisitPage("https://google.com", "Google")
	browser.VisitPage("https://github.com", "GitHub")
	browser.VisitPage("https://stackoverflow.com", "Stack Overflow")
	browser.VisitPage("https://reddit.com", "Reddit")
	
	browser.GetHistoryStatus()
	
	fmt.Println("\nNavigating back and forward:")
	browser.GoBack()
	browser.GoBack()
	browser.GetHistoryStatus()
	
	browser.GoForward()
	browser.VisitPage("https://news.ycombinator.com", "Hacker News")
	browser.GetHistoryStatus()

	fmt.Println("\n=== Function Call Stack Example ===")
	callStack := NewCallStack()
	
	fmt.Println("Simulating recursive factorial calculation:")
	result := simulateRecursiveFunction(callStack, 5, 0)
	fmt.Printf("Final result: %d\n", result)
	
	fmt.Println("\nSimulating nested function calls:")
	callStack = NewCallStack()
	callStack.PushFrame("main", map[string]interface{}{}, 1)
	callStack.SetLocalVariable("user", "Alice")
	
	callStack.PushFrame("processUser", map[string]interface{}{"userId": 123}, 15)
	callStack.SetLocalVariable("userData", map[string]string{"name": "Alice", "role": "admin"})
	
	callStack.PushFrame("validatePermissions", map[string]interface{}{"role": "admin"}, 45)
	callStack.SetLocalVariable("hasAccess", true)
	
	callStack.PrintStackTrace()
	
	fmt.Println("\nUnwinding the stack:")
	for callStack.GetStackDepth() > 0 {
		callStack.PopFrame()
	}

	fmt.Println("\n=== Undo/Redo Operations Example ===")
	undoSystem := NewUndoRedoSystem(10)
	
	fmt.Println("Simulating text editor operations:")
	undoSystem.ExecuteAction("INSERT", "Insert 'Hello'", map[string]interface{}{"text": "Hello", "position": 0})
	undoSystem.ExecuteAction("INSERT", "Insert ' World'", map[string]interface{}{"text": " World", "position": 5})
	undoSystem.ExecuteAction("FORMAT", "Make text bold", map[string]interface{}{"style": "bold", "range": "0-11"})
	undoSystem.ExecuteAction("INSERT", "Insert '!'", map[string]interface{}{"text": "!", "position": 11})
	undoSystem.ExecuteAction("DELETE", "Delete last character", map[string]interface{}{"position": 11, "count": 1})
	
	undoSystem.GetHistory()
	
	fmt.Println("\nUndo operations:")
	undoSystem.Undo()
	undoSystem.Undo()
	undoSystem.GetHistory()
	
	fmt.Println("\nRedo operations:")
	undoSystem.Redo()
	undoSystem.GetHistory()
	
	fmt.Println("\nExecuting new action (clears redo stack):")
	undoSystem.ExecuteAction("INSERT", "Insert '!!!'", map[string]interface{}{"text": "!!!", "position": 11})
	undoSystem.GetHistory()
	
	fmt.Printf("\nCan undo: %t, Can redo: %t\n", undoSystem.CanUndo(), undoSystem.CanRedo())
}

func main() {
	demonstrateStacks()
}