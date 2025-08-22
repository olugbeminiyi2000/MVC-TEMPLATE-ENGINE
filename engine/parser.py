from typing import List, Match, Tuple, Union

def parse_template_components(template_content: str, possible_patterns_match: List[Tuple[str, Match[str]]]) -> List[Tuple[str, Union[Match[str], None]]]:
    current_pattern_index: int = 0
    current_static_text: str = ""
    parsed_components: List[Tuple[str, Union[Match, None]]] = []
    possible_patterns_size: int = len(possible_patterns_match)

    for char_idx in range(len(template_content)):
        if current_pattern_index < possible_patterns_size:
            match_obj = possible_patterns_match[current_pattern_index][1]
            match_span = match_obj.span()
            start = match_span[0]
            end = match_span[1] - 1
        if char_idx >= start and char_idx <= end:
            if char_idx == match_span[1] - 1:
                parsed_components.append((current_static_text, ))
                parsed_components.append((match_obj.group(), match_obj))
                current_pattern_index += 1
                current_static_text = ""
        else:
            current_static_text += template_content[char_idx]
    else:
        if current_static_text:
            parsed_components.append(current_static_text)
            current_static_text = ""
    return parsed_components
