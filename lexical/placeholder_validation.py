from typing import List, Tuple, Dict, Any

def all_placeholders_exist(data_to_render: Dict[str, Any], component_list: List[str]) -> Tuple[bool, Any]:
    for component in component_list:
        if component in ['NOT', 'AND', 'OR']:
            continue
        try:
            _ = data_to_render[component]
        except KeyError as e:
            return (False, component)
    else:
        return (True, None)

def variable_exists(data_to_render: Dict[str, Any], variable: str) -> Tuple[bool, Any]:
    if variable in data_to_render:
        return (True, None)
    else:
        return (False, variable) 