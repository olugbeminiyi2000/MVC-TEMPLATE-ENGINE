from typing import List, Tuple, Dict, Any

def does_placeholder_exist(rendered_data: Dict[str, Any], component_list: List[str]) -> Tuple[bool, Any]:
    # iterate through component list
    # if element is logic; skip
    # if element is a variable check it existence
    for component in component_list:
        if component in ['NOT', 'AND', 'OR']:
            continue
        try:
            _ = rendered_data[component]
        except KeyError as e:
            return (False, component)
    else:
        return (True, None)
