"""
Source code capture functionality for snapshotplot.

This module handles capturing source code using Python's inspect module
to get function names, file paths, and line numbers.
"""

import inspect
import os
from typing import Dict, Any, Optional, Tuple


def get_calling_info(depth: int = 2) -> Dict[str, Any]:
    """
    Get information about the calling function and file.
    
    Args:
        depth: Stack depth to look for the calling function (default: 2)
        
    Returns:
        Dict containing function name, filename, line number, and source code
    """
    try:
        # Get the frame at the specified depth
        frame = inspect.currentframe()
        for _ in range(depth):
            if frame is None:
                break
            frame = frame.f_back
        
        if frame is None:
            return _get_fallback_info()
        
        # Extract information from the frame
        function_name = frame.f_code.co_name
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno
        
        # Get the function object if possible
        func_obj = None
        if function_name != '<module>':
            # Try to get the function object from the frame
            for name, obj in frame.f_globals.items():
                if inspect.isfunction(obj) and obj.__name__ == function_name:
                    func_obj = obj
                    break
        
        # Get source code
        source_code = _get_source_code(func_obj, filename, line_number)
        
        return {
            'function_name': function_name,
            'filename': os.path.basename(filename),
            'full_path': filename,
            'line_number': line_number,
            'source_code': source_code,
            'module_name': _get_module_name(filename)
        }
        
    except Exception as e:
        # Fallback if anything goes wrong
        return _get_fallback_info()
    finally:
        # Clean up frame reference
        if 'frame' in locals():
            del frame


def _get_source_code(func_obj: Optional[Any], filename: str, line_number: int) -> str:
    """
    Get the source code for the function or file.
    
    Args:
        func_obj: Function object (if available)
        filename: Path to the source file
        line_number: Line number where the call was made
        
    Returns:
        str: Source code
    """
    try:
        if func_obj is not None and hasattr(func_obj, '__code__'):
            # Get source for the specific function
            source_lines, _ = inspect.getsourcelines(func_obj)
            return ''.join(source_lines)
        else:
            # Get source for the entire file
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception:
        # Fallback: return a placeholder
        return f"# Source code not available for {filename}"


def _get_module_name(filename: str) -> str:
    """
    Extract module name from filename.
    
    Args:
        filename: Full path to the file
        
    Returns:
        str: Module name
    """
    basename = os.path.basename(filename)
    if basename.endswith('.py'):
        return basename[:-3]
    return basename


def _get_fallback_info() -> Dict[str, Any]:
    """
    Get fallback information when inspection fails.
    
    Returns:
        Dict with fallback values
    """
    return {
        'function_name': 'unknown_function',
        'filename': 'unknown_file.py',
        'full_path': 'unknown_path',
        'line_number': 0,
        'source_code': '# Source code not available',
        'module_name': 'unknown_module'
    }


def get_function_signature(func_obj: Any) -> str:
    """
    Get the function signature as a string.
    
    Args:
        func_obj: Function object
        
    Returns:
        str: Function signature
    """
    try:
        return str(inspect.signature(func_obj))
    except Exception:
        return "()"


def get_docstring(func_obj: Any) -> str:
    """
    Get the function's docstring.
    
    Args:
        func_obj: Function object
        
    Returns:
        str: Function docstring or empty string
    """
    try:
        return inspect.getdoc(func_obj) or ""
    except Exception:
        return "" 