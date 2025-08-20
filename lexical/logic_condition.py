"""
Logic Chain Builder for Template Engine

This file is responsible for building a logic chain (linked list) from a list of logic tokens (NOT, AND, OR), using the node classes.
"""

from __future__ import annotations
from typing import Dict, Union, List
from lexical.logic_nodes import logicNode, notNode, andNode, orNode 


def get_logic_chain(condition_tokens: List[str]) -> Union[logicNode, None]:
    """
    Build a logic chain from a list of logic tokens.
    For each token, create the corresponding node (NOT, AND, OR) and add it to its chain.
    After all nodes are created, join the chains in the order: NOT -> AND -> OR.
    Return the head of the combined logic chain.
    """
    num_tokens: int = len(condition_tokens)

    # create a chain for each logic operator
    for i in range(num_tokens):
        logic_token: str = condition_tokens[i]
        if logic_token == "OR":
            or_node: orNode = orNode(logic_token, i)
            orNode.add_new_or_node(or_node)
        elif logic_token == "AND":
            and_node: andNode = andNode(logic_token, i)
            andNode.add_new_and_node(and_node)
        elif logic_token == "NOT":
            not_node: notNode = notNode(logic_token, i)
            notNode.add_new_not_node(not_node)
        else:
            pass
    
    logic_chain_map: Dict[int, List[Union[notNode, andNode, orNode]]] = {0: [notNode.get_not_head(), notNode.get_not_current()], 1: [andNode.get_and_head(), andNode.get_and_current()], 2: [orNode.get_or_head(), orNode.get_or_current()]}

    logicNode.build_logic_chain(logic_chain_map)
    return logicNode.get_logic_head()

    

