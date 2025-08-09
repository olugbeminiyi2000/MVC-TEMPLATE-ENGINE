"""
Placeholder and Variable Existence Helpers

This file contains helper functions for checking if variables/placeholders exist in the provided context data.
"""

from typing import List, Tuple, Dict, Any

def all_placeholders_exist(context_data: Dict[str, Any], variable_names: List[str]) -> Tuple[bool, Any]:
    """
    Check if all variable names in the list exist in the context data.
    Skips logic operators (NOT, AND, OR). Returns (True, None) if all exist, otherwise (False, missing_variable).
    """
    for variable_name in variable_names:
        if variable_name in ['NOT', 'AND', 'OR']:
            continue
        try:
            _ = context_data[variable_name]
        except KeyError as e:
            return (False, variable_name)
    else:
        return (True, None)

def variable_exists(context_data: Dict[str, Any], context_data_temp: Dict[str, Any], variable_name: str) -> Tuple[bool, Any]:
    """
    Check if a single variable exists in the context data. Returns (True, None) if it exists, otherwise (False, variable_name).
    """
    if variable_name in context_data or variable_name in context_data_temp:
        return (True, None)
    else:
        return (False, variable_name) 