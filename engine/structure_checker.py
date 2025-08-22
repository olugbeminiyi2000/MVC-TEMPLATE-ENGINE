from typing import List, Match, Tuple
from engine_core.exceptions import StructureError

def check_condition_structure(condition_blocks: List[Tuple[str, Match[str]]]) -> None:
    condition_position: int = 0
    condition_length: int = len(condition_blocks)
    last_condition_position: int = condition_length - 1
    condition_start_list: List[Tuple[str, Match]] = []
    condition_start: int = 0
    while condition_position <= last_condition_position:
        try:
            if condition_start == 0:
                initial_condition_tuple = condition_blocks[condition_position]
                if initial_condition_tuple[0] != "if_statement":
                    raise StructureError("Block should start with {{% IF STATEMENT %}} not {}".format(initial_condition_tuple[1].group()))
                
            current_condition_tuple = condition_blocks[condition_position]
            if current_condition_tuple[0] == "if_statement":
                condition_start += 1
                condition_start_list.append(current_condition_tuple)
            elif current_condition_tuple[0] == "endif_statement":
                condition_start -= 1
                del condition_start_list[-1]
            
            condition_position += 1
        except StructureError:
            raise
    else:
        try:
            if condition_start != 0:
                last_type, last_match = condition_start_list[-1]
                raise StructureError(
                    "Missing a {{% ENDIF %}} block for {} at {}"
                    .format(last_type, last_match.group())
                )
        except StructureError:
            raise

def check_loop_structure(loop_blocks: List[Tuple[str, Match[str]]]) -> None:
    loop_position: int = 0
    loop_length: int = len(loop_blocks)
    last_loop_position: int = loop_length - 1
    loop_start_list: List[Tuple[str, Match]] = []
    loop_start: int = 0
    while loop_position <= last_loop_position:
        try:
            if loop_start == 0:
                initial_loop_tuple = loop_blocks[loop_position]
                if initial_loop_tuple[0] != "for_loop_statement":
                    raise StructureError("Block should start with {{% FOR STATEMENT %}} not {}".format(initial_loop_tuple[1].group()))
                
            current_loop_tuple = loop_blocks[loop_position]
            if current_loop_tuple[0] == "for_loop_statement":
                loop_start += 1
                loop_start_list.append(current_loop_tuple)
            elif current_loop_tuple[0] == "endfor_loop_statement":
                loop_start -= 1
                del loop_start_list[-1]
            
            loop_position += 1
        except StructureError:
            raise
    else:
        try:
            if loop_start != 0:
                last_type, last_match = loop_start_list[-1]
                raise StructureError(
                    "Missing a {{% ENDFOR %}} block for {} at {} (span: {})"
                    .format(last_type, last_match.group(), last_match.span())
                )
        except StructureError:
            raise

