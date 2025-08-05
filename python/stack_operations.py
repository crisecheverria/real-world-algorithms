from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import time
import traceback

class Page:
    def __init__(self, url: str, title: str):
        self.url = url
        self.title = title
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"Page(url='{self.url}', title='{self.title}')"

class BrowserHistory:
    def __init__(self):
        self.back_stack: List[Page] = []
        self.forward_stack: List[Page] = []
        self.current_page: Optional[Page] = None
    
    def visit_page(self, url: str, title: str) -> None:
        """Visit a new page, adding current page to back history"""
        if self.current_page:
            self.back_stack.append(self.current_page)
        
        new_page = Page(url, title)
        self.current_page = new_page
        
        # Clear forward history when visiting new page
        self.forward_stack.clear()
        
        print(f"Visited: {title} ({url})")
    
    def go_back(self) -> bool:
        """Go back to previous page"""
        if not self.back_stack:
            print("Cannot go back - no pages in history")
            return False
        
        if self.current_page:
            self.forward_stack.append(self.current_page)
        
        previous_page = self.back_stack.pop()
        self.current_page = previous_page
        
        print(f"Went back to: {previous_page.title} ({previous_page.url})")
        return True
    
    def go_forward(self) -> bool:
        """Go forward to next page"""
        if not self.forward_stack:
            print("Cannot go forward - no pages in forward history")
            return False
        
        if self.current_page:
            self.back_stack.append(self.current_page)
        
        next_page = self.forward_stack.pop()
        self.current_page = next_page
        
        print(f"Went forward to: {next_page.title} ({next_page.url})")
        return True
    
    def get_current_page(self) -> Optional[Page]:
        return self.current_page
    
    def can_go_back(self) -> bool:
        return len(self.back_stack) > 0
    
    def can_go_forward(self) -> bool:
        return len(self.forward_stack) > 0
    
    def get_history_status(self) -> None:
        print("Browser History Status:")
        if self.current_page:
            print(f"  Current: {self.current_page.title} ({self.current_page.url})")
        else:
            print("  Current: No page loaded")
        
        print(f"  Back stack: {len(self.back_stack)} pages")
        print(f"  Forward stack: {len(self.forward_stack)} pages")
        
        if self.back_stack:
            recent_pages = [page.title for page in self.back_stack[-3:]]
            print(f"  Recent back pages: {' -> '.join(recent_pages)}")
    
    def clear_history(self) -> None:
        """Clear all browser history"""
        self.back_stack.clear()
        self.forward_stack.clear()
        print("Browser history cleared")
    
    def get_back_history(self) -> List[Page]:
        """Get copy of back history"""
        return self.back_stack.copy()
    
    def get_forward_history(self) -> List[Page]:
        """Get copy of forward history"""
        return self.forward_stack.copy()
    
    def get_history_summary(self) -> Dict[str, Any]:
        """Get summary of browser history"""
        total_pages = len(self.back_stack) + len(self.forward_stack)
        if self.current_page:
            total_pages += 1
        
        return {
            "total_pages_visited": total_pages,
            "back_stack_size": len(self.back_stack),
            "forward_stack_size": len(self.forward_stack),
            "current_page": self.current_page.title if self.current_page else None,
            "can_navigate_back": self.can_go_back(),
            "can_navigate_forward": self.can_go_forward()
        }

class CallFrame:
    def __init__(self, function_name: str, parameters: Dict[str, Any] = None, line_number: int = 0):
        self.function_name = function_name
        self.parameters = parameters or {}
        self.local_vars: Dict[str, Any] = {}
        self.return_address = 0
        self.line_number = line_number
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f"CallFrame(function='{self.function_name}', line={self.line_number})"

class CallStack:
    def __init__(self):
        self.frames: List[CallFrame] = []
    
    def push_frame(self, func_name: str, params: Dict[str, Any] = None, line_num: int = 0) -> None:
        """Push a new call frame onto the stack"""
        frame = CallFrame(func_name, params, line_num)
        frame.return_address = len(self.frames)
        self.frames.append(frame)
        print(f"Called: {func_name}() at line {line_num}")
    
    def pop_frame(self) -> Optional[CallFrame]:
        """Pop the top call frame from the stack"""
        if not self.frames:
            return None
        
        frame = self.frames.pop()
        print(f"Returned from: {frame.function_name}()")
        return frame
    
    def get_current_frame(self) -> Optional[CallFrame]:
        """Get the current (top) call frame"""
        return self.frames[-1] if self.frames else None
    
    def set_local_variable(self, name: str, value: Any) -> None:
        """Set a local variable in the current frame"""
        frame = self.get_current_frame()
        if frame:
            frame.local_vars[name] = value
    
    def get_local_variable(self, name: str) -> Any:
        """Get a local variable from the current frame"""
        frame = self.get_current_frame()
        return frame.local_vars.get(name) if frame else None
    
    def print_stack_trace(self) -> None:
        """Print the current stack trace"""
        print("Stack Trace:")
        for i in range(len(self.frames) - 1, -1, -1):
            frame = self.frames[i]
            print(f"  at {frame.function_name}() line {frame.line_number}")
            
            if frame.parameters:
                print(f"    Parameters: {frame.parameters}")
            if frame.local_vars:
                print(f"    Local vars: {frame.local_vars}")
    
    def get_stack_depth(self) -> int:
        """Get the current stack depth"""
        return len(self.frames)
    
    def has_frame(self, function_name: str) -> bool:
        """Check if a function is currently on the stack"""
        return any(frame.function_name == function_name for frame in self.frames)
    
    def get_frame_by_function(self, function_name: str) -> Optional[CallFrame]:
        """Get the most recent frame for a specific function"""
        for frame in reversed(self.frames):
            if frame.function_name == function_name:
                return frame
        return None
    
    def get_call_chain(self) -> List[str]:
        """Get the chain of function calls"""
        return [frame.function_name for frame in self.frames]
    
    def detect_recursion(self) -> Dict[str, int]:
        """Detect recursive function calls and their depth"""
        function_counts = {}
        for frame in self.frames:
            function_counts[frame.function_name] = function_counts.get(frame.function_name, 0) + 1
        
        return {func: count for func, count in function_counts.items() if count > 1}

class Action:
    def __init__(self, action_type: str, description: str, data: Any, undo_data: Any = None):
        self.type = action_type
        self.description = description
        self.data = data
        self.undo_data = undo_data
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"Action(type='{self.type}', description='{self.description}')"

class UndoRedoSystem:
    def __init__(self, max_size: int = 50):
        self.undo_stack: List[Action] = []
        self.redo_stack: List[Action] = []
        self.max_size = max_size
    
    def execute_action(self, action_type: str, description: str, data: Any, undo_data: Any = None) -> None:
        """Execute an action and add it to the undo stack"""
        action = Action(action_type, description, data, undo_data)
        self.undo_stack.append(action)
        
        # Maintain max size
        if len(self.undo_stack) > self.max_size:
            self.undo_stack.pop(0)
        
        # Clear redo stack when new action is executed
        self.redo_stack.clear()
        
        print(f"Executed: {action_type} - {description}")
    
    def undo(self) -> Optional[Action]:
        """Undo the last action"""
        if not self.undo_stack:
            print("Nothing to undo")
            return None
        
        action = self.undo_stack.pop()
        self.redo_stack.append(action)
        
        print(f"Undid: {action.type} - {action.description}")
        return action
    
    def redo(self) -> Optional[Action]:
        """Redo the last undone action"""
        if not self.redo_stack:
            print("Nothing to redo")
            return None
        
        action = self.redo_stack.pop()
        self.undo_stack.append(action)
        
        print(f"Redid: {action.type} - {action.description}")
        return action
    
    def get_history(self) -> None:
        """Print the current undo/redo history"""
        print("Undo/Redo System Status:")
        print(f"  Undo stack: {len(self.undo_stack)} actions")
        print(f"  Redo stack: {len(self.redo_stack)} actions")
        
        if self.undo_stack:
            print("  Recent actions (newest first):")
            recent_actions = list(reversed(self.undo_stack[-5:]))
            for i, action in enumerate(recent_actions, 1):
                time_str = action.timestamp.strftime("%H:%M:%S")
                print(f"    {i}. {action.type}: {action.description} ({time_str})")
    
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
    
    def clear_history(self) -> None:
        """Clear all undo/redo history"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        print("Cleared all undo/redo history")
    
    def get_undo_actions(self) -> List[Action]:
        """Get copy of undo actions"""
        return self.undo_stack.copy()
    
    def get_redo_actions(self) -> List[Action]:
        """Get copy of redo actions"""
        return self.redo_stack.copy()
    
    def peek(self) -> Optional[Action]:
        """Peek at the last action without removing it"""
        return self.undo_stack[-1] if self.undo_stack else None
    
    def get_action_count(self) -> int:
        """Get total number of actions tracked"""
        return len(self.undo_stack) + len(self.redo_stack)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the undo/redo system"""
        action_types = {}
        for action in self.undo_stack + self.redo_stack:
            action_types[action.type] = action_types.get(action.type, 0) + 1
        
        return {
            "total_actions": self.get_action_count(),
            "undo_actions": len(self.undo_stack),
            "redo_actions": len(self.redo_stack),
            "action_types": action_types,
            "can_undo": self.can_undo(),
            "can_redo": self.can_redo(),
            "max_size": self.max_size
        }

class TextEditor:
    """Text editor implementation using undo/redo system"""
    
    def __init__(self):
        self.content = ""
        self.cursor_position = 0
        self.undo_redo_system = UndoRedoSystem(100)
        self.selection_start = 0
        self.selection_end = 0
    
    def insert(self, text: str, position: Optional[int] = None) -> None:
        """Insert text at specified position or cursor"""
        pos = position if position is not None else self.cursor_position
        
        # Store undo data
        undo_data = {
            "type": "delete",
            "position": pos,
            "length": len(text)
        }
        
        # Execute the insertion
        self.content = self.content[:pos] + text + self.content[pos:]
        self.cursor_position = pos + len(text)
        
        # Record the action
        action_data = {
            "type": "insert",
            "position": pos,
            "text": text
        }
        
        self.undo_redo_system.execute_action(
            "INSERT",
            f"Insert '{text}' at position {pos}",
            action_data,
            undo_data
        )
    
    def delete(self, position: int, length: int) -> None:
        """Delete text at specified position"""
        deleted_text = self.content[position:position + length]
        
        # Store undo data
        undo_data = {
            "type": "insert",
            "position": position,
            "text": deleted_text
        }
        
        # Execute the deletion
        self.content = self.content[:position] + self.content[position + length:]
        self.cursor_position = position
        
        # Record the action
        action_data = {
            "type": "delete",
            "position": position,
            "length": length,
            "deleted_text": deleted_text
        }
        
        self.undo_redo_system.execute_action(
            "DELETE",
            f"Delete '{deleted_text}' at position {position}",
            action_data,
            undo_data
        )
    
    def replace(self, position: int, length: int, new_text: str) -> None:
        """Replace text at specified position"""
        old_text = self.content[position:position + length]
        
        # Store undo data
        undo_data = {
            "type": "replace",
            "position": position,
            "length": len(new_text),
            "text": old_text
        }
        
        # Execute the replacement
        self.content = self.content[:position] + new_text + self.content[position + length:]
        self.cursor_position = position + len(new_text)
        
        # Record the action
        action_data = {
            "type": "replace",
            "position": position,
            "length": length,
            "old_text": old_text,
            "new_text": new_text
        }
        
        self.undo_redo_system.execute_action(
            "REPLACE",
            f"Replace '{old_text}' with '{new_text}' at position {position}",
            action_data,
            undo_data
        )
    
    def undo(self) -> None:
        """Undo the last operation"""
        action = self.undo_redo_system.undo()
        if action and action.undo_data:
            self._apply_operation(action.undo_data)
    
    def redo(self) -> None:
        """Redo the last undone operation"""
        action = self.undo_redo_system.redo()
        if action and action.data:
            self._apply_operation(action.data)
    
    def _apply_operation(self, operation: Dict[str, Any]) -> None:
        """Apply an operation to the text content"""
        op_type = operation["type"]
        
        if op_type == "insert":
            pos = operation["position"]
            text = operation["text"]
            self.content = self.content[:pos] + text + self.content[pos:]
            self.cursor_position = pos + len(text)
        
        elif op_type == "delete":
            pos = operation["position"]
            length = operation["length"]
            self.content = self.content[:pos] + self.content[pos + length:]
            self.cursor_position = pos
        
        elif op_type == "replace":
            pos = operation["position"]
            length = operation["length"]
            text = operation["text"]
            self.content = self.content[:pos] + text + self.content[pos + length:]
            self.cursor_position = pos + len(text)
    
    def get_content(self) -> str:
        return self.content
    
    def get_undo_redo_status(self) -> None:
        self.undo_redo_system.get_history()
    
    def can_undo(self) -> bool:
        return self.undo_redo_system.can_undo()
    
    def can_redo(self) -> bool:
        return self.undo_redo_system.can_redo()
    
    def get_cursor_position(self) -> int:
        return self.cursor_position
    
    def set_cursor_position(self, position: int) -> None:
        self.cursor_position = max(0, min(position, len(self.content)))

def simulate_recursive_function(call_stack: CallStack, n: int, depth: int = 0) -> int:
    """Simulate a recursive factorial function with call stack tracking"""
    call_stack.push_frame('factorial', {'n': n}, 100 + depth)
    
    current_frame = call_stack.get_current_frame()
    if current_frame:
        current_frame.local_vars['depth'] = depth
    
    if n <= 1:
        call_stack.set_local_variable('result', 1)
        result = 1
    else:
        call_stack.set_local_variable('temp', n - 1)
        temp = simulate_recursive_function(call_stack, n - 1, depth + 1)
        result = n * temp
        call_stack.set_local_variable('result', result)
    
    call_stack.pop_frame()
    return result

def simulate_complex_call_chain(call_stack: CallStack) -> None:
    """Simulate a complex chain of function calls"""
    call_stack.push_frame('main', {}, 1)
    call_stack.set_local_variable('app_state', 'initializing')
    
    call_stack.push_frame('initialize_app', {'config_file': 'app.config'}, 10)
    call_stack.set_local_variable('config', {'db_host': 'localhost', 'port': 8080})
    
    call_stack.push_frame('setup_database', {'host': 'localhost'}, 25)
    call_stack.set_local_variable('connection', 'db_connection_object')
    
    call_stack.push_frame('migrate_schema', {'version': '2.1'}, 45)
    call_stack.set_local_variable('migration_status', 'in_progress')
    
    call_stack.push_frame('validate_schema', {}, 67)
    call_stack.set_local_variable('validation_errors', [])
    
    # Show recursion detection
    recursion_info = call_stack.detect_recursion()
    if recursion_info:
        print(f"Recursion detected: {recursion_info}")

def demonstrate_stacks():
    print("=== Browser Navigation History Example ===")
    browser = BrowserHistory()
    
    # Simulate browsing session
    websites = [
        ("https://google.com", "Google"),
        ("https://github.com", "GitHub"), 
        ("https://stackoverflow.com", "Stack Overflow"),
        ("https://python.org", "Python.org"),
        ("https://docs.python.org", "Python Documentation"),
        ("https://realpython.com", "Real Python")
    ]
    
    for url, title in websites:
        browser.visit_page(url, title)
    
    browser.get_history_status()
    
    print("\nNavigating back and forward:")
    browser.go_back()
    browser.go_back()
    browser.go_back()
    browser.get_history_status()
    
    browser.go_forward()
    browser.go_forward()
    browser.visit_page("https://news.ycombinator.com", "Hacker News")
    browser.get_history_status()
    
    summary = browser.get_history_summary()
    print(f"\nHistory Summary: {summary}")

    print("\n=== Function Call Stack Example ===")
    call_stack = CallStack()
    
    print("Simulating recursive factorial calculation:")
    result = simulate_recursive_function(call_stack, 5)
    print(f"Final result: {result}")
    
    print("\nSimulating complex application startup:")
    complex_call_stack = CallStack()
    simulate_complex_call_chain(complex_call_stack)
    
    print(f"\nCall chain: {' -> '.join(complex_call_stack.get_call_chain())}")
    complex_call_stack.print_stack_trace()
    
    print("\nUnwinding the stack:")
    while complex_call_stack.get_stack_depth() > 0:
        complex_call_stack.pop_frame()

    print("\n=== Text Editor Undo/Redo Example ===")
    editor = TextEditor()
    
    print("Simulating text editing session:")
    editor.insert("Hello")
    print(f'Content: "{editor.get_content()}"')
    
    editor.insert(" World")
    print(f'Content: "{editor.get_content()}"')
    
    editor.insert("!", 11)
    print(f'Content: "{editor.get_content()}"')
    
    editor.delete(5, 6)  # Delete " World"
    print(f'Content: "{editor.get_content()}"')
    
    editor.insert(" Python")
    print(f'Content: "{editor.get_content()}"')
    
    editor.replace(6, 6, "Amazing Python")
    print(f'Content: "{editor.get_content()}"')
    
    editor.get_undo_redo_status()
    
    print("\nUndo operations:")
    editor.undo()
    print(f'Content after undo: "{editor.get_content()}"')
    
    editor.undo()
    print(f'Content after undo: "{editor.get_content()}"')
    
    editor.undo()
    print(f'Content after undo: "{editor.get_content()}"')
    
    print("\nRedo operations:")
    editor.redo()
    print(f'Content after redo: "{editor.get_content()}"')
    
    editor.redo()
    print(f'Content after redo: "{editor.get_content()}"')
    
    editor.get_undo_redo_status()

    print("\n=== Advanced Undo/Redo System Example ===")
    undo_system = UndoRedoSystem(15)
    
    # Simulate graphics application operations
    operations = [
        ("DRAW_RECTANGLE", "Draw rectangle at (10,10)", {"shape": "rect", "x": 10, "y": 10, "w": 50, "h": 30}),
        ("DRAW_CIRCLE", "Draw circle at (100,100)", {"shape": "circle", "x": 100, "y": 100, "r": 25}),
        ("CHANGE_COLOR", "Change rectangle to blue", {"object_id": 1, "color": "blue", "old_color": "black"}),
        ("MOVE_OBJECT", "Move circle to (120,120)", {"object_id": 2, "new_pos": [120, 120], "old_pos": [100, 100]}),
        ("DRAW_LINE", "Draw line from (0,0) to (200,200)", {"shape": "line", "start": [0, 0], "end": [200, 200]}),
        ("GROUP_OBJECTS", "Group rectangle and circle", {"objects": [1, 2], "group_id": 3}),
        ("RESIZE_OBJECT", "Resize rectangle", {"object_id": 1, "new_size": [60, 40], "old_size": [50, 30]}),
        ("DELETE_OBJECT", "Delete line", {"object_id": 5, "backup_data": {"shape": "line", "start": [0, 0], "end": [200, 200]}}),
    ]
    
    for op_type, description, data in operations:
        undo_system.execute_action(op_type, description, data)
    
    undo_system.get_history()
    
    print("\nUndo last 3 operations:")
    for _ in range(3):
        undo_system.undo()
    
    print("\nExecute new operation (clears redo stack):")
    undo_system.execute_action("DRAW_TEXT", "Add text 'Hello World'", 
                             {"text": "Hello World", "x": 50, "y": 50, "font": "Arial"})
    
    stats = undo_system.get_statistics()
    print(f"\nSystem Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nFinal status - Can undo: {undo_system.can_undo()}, Can redo: {undo_system.can_redo()}")

if __name__ == "__main__":
    demonstrate_stacks()