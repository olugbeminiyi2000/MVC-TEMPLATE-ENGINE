from __future__ import annotations
from typing import Optional, Dict, Any, Union, List
from lexical.logic_nodes import logicNode, notNode, andNode, orNode 

logic_iter: int = 3

# Logic node classes moved to logic_nodes.py for better modularity.

def get_logic_chain(condition_tokens: List[str]) -> Union[logicNode, None]:
    token_len: int = len(condition_tokens)

    # create a chain for each logic operator
    for i in range(token_len):
        logic: str = condition_tokens[i]
        if logic == "OR":
            or_node: orNode = orNode(logic, i)
            orNode.add_new_or_node(or_node)
        elif logic == "AND":
            and_node: andNode = andNode(logic, i)
            andNode.add_new_and_node(and_node)
        elif logic == "NOT":
            not_node: notNode = notNode(logic, i)
            notNode.add_new_not_node(not_node)
        else:
            pass
    
    # create a dict for getting the head(head) and tail(current) for each logic
    # a the key number really matters we want (not -> and -> or)
    logic_dict: Dict[int, List[Union[notNode, andNode, orNode]]] = {0: [notNode.get_not_head(), notNode.get_not_current()], 1: [andNode.get_and_head(), andNode.get_and_current()], 2: [orNode.get_or_head(), orNode.get_or_current()]}

    # pass this dictionary logic_dict to the logic class build_logic_chain class method
    logicNode.build_logic_chain(logic_dict)
    return logicNode.get_logic_head()

    

