from __future__ import annotations
from typing import Optional, Dict, Any, Union, List

"""
Logic Node Classes for Template Engine

Defines the node structures for representing logic operators (NOT, AND, OR) as linked lists.
Each node type manages its own chain, and the base logicNode class manages the overall logic chain.
"""

# MAX_LOGIC_OPERATOR_TYPES represents the number of logic operators (NOT, AND, OR).
# It is used to limit the maximum number of logic chains that can be joined together.
MAX_LOGIC_OPERATOR_TYPES: int = 3

class logicNode:
    """
    Base class for all logic nodes in the logic chain.
    Manages the head/current pointers and provides methods to build and display the logic chain.
    """
    __logic_head_node: Union[logicNode, None] = None
    __logic_current_node: Union[logicNode, None] = None

    @classmethod
    def reset_logic_head(cls) -> None:
        """Reset the head and current pointers of the logic chain to None."""
        cls.__logic_head_node = None
        cls.__logic_current_node = None

    @classmethod
    def get_logic_head(cls) -> Union[logicNode, None]:
        """Return the head node of the logic chain."""
        return cls.__logic_head_node
    
    @classmethod
    def build_logic_chain(cls, logic_chain_map: Dict[int, List[Union['notNode', 'andNode', 'orNode']]]) -> None:
        """
        Build the logic chain by joining the NOT, AND, and OR chains in order.
        The number of chains joined is limited by MAX_LOGIC_OPERATOR_TYPES.
        """
        for i in range(0, MAX_LOGIC_OPERATOR_TYPES):
            if not cls.__logic_head_node:
                cls.__logic_head_node = logic_chain_map[i][0]
                cls.__logic_current_node = logic_chain_map[i][1]
            else:
                if cls.__logic_current_node:
                    cls.__logic_current_node.next = logic_chain_map[i][0]
                    cls.__logic_current_node = logic_chain_map[i][1]
    
    @classmethod
    def display_logic_chain(cls) -> None:
        """Print a string representation of the current logic chain for debugging."""
        node_cursor: Union[logicNode, None] = cls.__logic_head_node
        chain_repr = ""
        while node_cursor is not None:
            node_data = getattr(node_cursor, "data", None)
            next_node_repr = "None" if getattr(node_cursor, "next", None) is None else "node"
            chain_repr += f"node{{{node_data}, {next_node_repr}}} -> "
            node_cursor = getattr(node_cursor, "next", None)
        chain_repr += "None"
        print(chain_repr)

class notNode(logicNode):
    """
    Node representing the NOT logic operator.
    Manages its own chain of NOT nodes.
    """
    __not_head_node: Optional['notNode'] = None
    __not_current_node: Optional['notNode'] = None

    def __init__(self, data: str, position: int) -> None:
        self.next: Optional['notNode'] = None
        self.data: Dict[str, Any]  = {"position": position, "data": data}

    @classmethod
    def reset_not_head(cls) -> None:
        """Reset the head and current pointers of the NOT chain to None."""
        cls.__not_head_node = None
        cls.__not_current_node = None

    @classmethod
    def get_not_head(cls) -> Union['notNode', None]:
        """Return the head node of the NOT chain."""
        return cls.__not_head_node

    @classmethod
    def get_not_current(cls) -> Union['notNode', None]:
        """Return the current node of the NOT chain."""
        return cls.__not_current_node
    
    @classmethod
    def add_new_not_node(cls, new_not_node: 'notNode') -> None:
        """Add a new NOT node to the end of the NOT chain."""
        not_head_node: Union['notNode', None] = cls.__not_head_node
        if not not_head_node:
            cls.__not_head_node = new_not_node
            cls.__not_current_node = new_not_node
        else:
            current_not_node: 'notNode' = cls.__not_current_node
            current_not_node.next = new_not_node
            cls.__not_current_node = new_not_node

class andNode(logicNode):
    __and_head_node: Optional['andNode'] = None
    __and_current_node: Optional['andNode'] = None

    def __init__(self, data: str, position: int) -> None:
        self.next: Optional['andNode'] = None
        self.data: Dict[str, Any]  = {"position": position, "data": data}
    
    @classmethod
    def reset_and_head(cls) -> None:
        cls.__and_head_node = None
        cls.__and_current_node = None

    @classmethod
    def get_and_head(cls) -> Union['andNode', None]:
        return cls.__and_head_node
    
    @classmethod
    def get_and_current(cls) -> Union['andNode', None]:
        return cls.__and_current_node
    
    @classmethod
    def add_new_and_node(cls, new_and_node: 'andNode') -> None:
        and_head_node: Union['andNode', None] = cls.__and_head_node
        if not and_head_node:
            cls.__and_head_node = new_and_node
            cls.__and_current_node = new_and_node
        else:
            current_and_node: 'andNode' = cls.__and_current_node
            current_and_node.next = new_and_node
            cls.__and_current_node = new_and_node

class orNode(logicNode):
    __or_head_node: Optional['orNode'] = None
    __or_current_node: Optional['orNode'] = None

    def __init__(self, data: str, position: int) -> None:
        self.next: Optional['orNode'] = None
        self.data: Dict[str, Any]  = {"position": position, "data": data}
    
    @classmethod
    def reset_or_head(cls) -> None:
        cls.__or_head_node = None
        cls.__or_current_node = None

    @classmethod
    def get_or_head(cls) -> Union['orNode', None]:
        return cls.__or_head_node
    
    @classmethod
    def get_or_current(cls) -> Union['orNode', None]:
        return cls.__or_current_node
    
    @classmethod
    def add_new_or_node(cls, new_or_node: 'orNode') -> None:
        or_head_node: Union['orNode', None] = cls.__or_head_node
        if not or_head_node:
            cls.__or_head_node = new_or_node
            cls.__or_current_node = new_or_node
        else:
            current_or_node: 'orNode' = cls.__or_current_node
            current_or_node.next = new_or_node
            cls.__or_current_node = new_or_node 