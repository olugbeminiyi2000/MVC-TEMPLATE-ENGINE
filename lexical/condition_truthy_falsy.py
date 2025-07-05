"""
Logic Expression Evaluator for Template Engine

This file evaluates the truthiness or falsiness of logic expressions represented by logic node chains.
"""

from lexical.logic_condition import logicNode
from typing import Dict, Union, Any, List

class RangeDict(Dict):
    """
    Custom dictionary for managing evaluation ranges in logic expressions.
    Used to track which parts of the component list have been evaluated and store intermediate results.
    """
    """
    Important!!!
    # NOTICE:
    # This class overrides __getitem__ to customize square bracket access.
    # Be aware that:
    # - del obj[key] calls __delitem__, not __getitem__
    # - obj.get(key) bypasses __getitem__ entirely (uses internal logic)
    # Therefore, use [] access if you want to trigger custom lookup logic.
    """

    def __getitem__(self, item) -> Union[range, None]:
        for key in self:
            if item in key:
                return key
        return None
    
    def mutate_collection_none(self, range_start: int, range_stop: int, result: bool) -> None:
        self[range(range_start, range_stop + 1)] = result

    def mutate_collection_one(self, dynamic_range_key: range, range_start: int, range_stop: int, result: bool) -> None:
        new_start: int = range_start if range_start < dynamic_range_key.start else dynamic_range_key.start
        new_stop: int = range_stop + 1 if range_stop > dynamic_range_key.stop - 1 else dynamic_range_key.stop
        del self[dynamic_range_key]
        self[range(new_start, new_stop)] = result

    def mutate_collection_two(self, before_range: Union[range, None], after_range: Union[range, None], result: bool) -> None:
        self[range(before_range.start, after_range.stop)] = result
        del self[before_range]
        del self[after_range]

    def get_final_result(self) -> Union[bool, None]:
        if len(self) == 1:
            for key in self:
                return self.get(key)
        return None
    



def get_truthy_falsy_logic(logic_node: logicNode, component_list: List[str], data_to_render: Dict[str, Any]) -> bool:
    """
    Evaluate the truthiness/falsiness of a logic expression represented by a logic node chain.
    Traverses the chain, applies NOT/AND/OR logic, and stores intermediate results in a RangeDict.
    Returns the final boolean result of the logic expression.
    """
    # cleanup previously used range dict object by creating a new one
    range_map_obj = RangeDict()
    
    # traverse through logic Node using the while loop
    # to get access the value in the data variables of logic (NOT|AND|OR)
    while logic_node:
        data: Dict[str, Any] = logic_node.data

        # solve for NOT logic
        if data['data'] == "NOT":
            logic_position: int = data['position']
            after_logic_position: int = logic_position + 1
            range_obj: Union[range, None] = range_map_obj[after_logic_position]
            # check if the value of variable at after_logic_position is a truthy or falsy value and apply the n(NOT) logic on it
            if not range_obj:
                boolean: bool = not bool(data_to_render.get(component_list[after_logic_position]))
                # now store the range position to know where you have operated to!
                range_map_obj.mutate_collection_none(logic_position, after_logic_position, boolean)

        elif data['data'] == "AND":
            logic_position: int = data['position']
            before_logic_position: int = logic_position - 1
            after_logic_position: int = logic_position + 1
            before_range: Union[range, None] = range_map_obj[before_logic_position]
            after_range: Union[range, None] = range_map_obj[after_logic_position]

            # solve for both before and after range objects being None
            if before_range is None and after_range is None:
                # check the value of both variable at before_logic_position and after_logic_position is either truthy or falsy value then apply the (AND) logic on it
                boolean: bool = bool(data_to_render.get(component_list[before_logic_position])) and bool(data_to_render.get(component_list[after_logic_position]))
                # now store the range position to know where you have operated to!
                range_map_obj.mutate_collection_none(before_logic_position, after_logic_position, boolean)
            elif before_range and after_range:
                # check the value of both before_range and after_range key values to know if it is a truthy or falsy value then apply the (AND) logic on it
                boolean: bool = bool(range_map_obj.get(before_range)) and bool(range_map_obj.get(after_range))
                # now store the range position to know where you have operated to!
                range_map_obj.mutate_collection_two(before_range, after_range, boolean)
            else:
                # here just one key is returned and the other None
                dynamically_pick_key = before_range if before_range else after_range
                dynamically_pick_position = after_logic_position if before_range else before_logic_position
                # check the value of the key if it is truthy or falsy and also that of the variable if it is truthy or falsy and apply the logic on it
                boolean: bool = bool(data_to_render.get(component_list[dynamically_pick_position])) and bool(range_map_obj.get(dynamically_pick_key))
                # now store the range position to know where you have operated to!
                range_map_obj.mutate_collection_one(dynamically_pick_key, before_logic_position, after_logic_position, boolean)
        elif data['data'] == "OR":
            logic_position: int = data['position']
            before_logic_position: int = logic_position - 1
            after_logic_position: int = logic_position + 1
            before_range: Union[range, None] = range_map_obj[before_logic_position]
            after_range: Union[range, None] = range_map_obj[after_logic_position]

            # solve for both before and after range objects being None
            if before_range is None and after_range is None:
                # check the value of both variable at before_logic_position and after_logic_position is either truthy or falsy value then apply the (OR) logic on it
                boolean: bool = bool(data_to_render.get(component_list[before_logic_position])) or bool(data_to_render.get(component_list[after_logic_position]))
                # now store the range position to know where you have operated to!
                range_map_obj.mutate_collection_none(before_logic_position, after_logic_position, boolean)
            elif before_range and after_range:
                # check the value of both before_range and after_range key values to know if it is a truthy or falsy value then apply the (OR) logic on it
                boolean: bool = bool(range_map_obj.get(before_range)) or bool(range_map_obj.get(after_range))
                # now store the range position to know where you have operated to!
                range_map_obj.mutate_collection_two(before_range, after_range, boolean)
            else:
                # here just one key is returned and the other None
                dynamically_pick_key = before_range if before_range else after_range
                dynamically_pick_position = after_logic_position if before_range else before_logic_position
                # check the value of the key if it is truthy or falsy and also that of the variable if it is truthy or falsy and apply the logic on it
                boolean: bool = bool(data_to_render.get(component_list[dynamically_pick_position])) or bool(range_map_obj.get(dynamically_pick_key))
                # now store the range position to know where you have operated to!
                range_map_obj.mutate_collection_one(dynamically_pick_key, before_logic_position, after_logic_position, boolean)
        
        logic_node: logicNode = logic_node.next
    return range_map_obj.get_final_result()

    

def get_truthy_falsy_no_logic(component_list: List[str], data_to_render: Dict[str, Any]) -> bool:
    """
    Fallback for evaluating a single-variable condition (no logic operators).
    Returns the truthiness of the first variable in the component list.
    """
    return bool(data_to_render.get(component_list[0]))

