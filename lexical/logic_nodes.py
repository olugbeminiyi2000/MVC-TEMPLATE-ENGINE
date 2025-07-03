from __future__ import annotations
from typing import Optional, Dict, Any, Union, List

logic_iter: int = 3

class logicNode:
    __logic_head_node: Union[logicNode, None] = None
    __logic_current_node: Union[logicNode, None] = None

    @classmethod
    def reset_logic_head(cls) -> None:
        cls.__logic_head_node = None
        cls.__logic_current_node = None

    @classmethod
    def get_logic_head(cls) -> Union[logicNode, None]:
        return cls.__logic_head_node
    
    @classmethod
    def build_logic_chain(cls, logic_dict: Dict[int, List[Union['notNode', 'andNode', 'orNode']]]) -> None:
        for i in range(0, logic_iter):
            if not cls.__logic_head_node:
                cls.__logic_head_node = logic_dict[i][0]
                cls.__logic_current_node = logic_dict[i][1]
            else:
                if cls.__logic_current_node:
                    cls.__logic_current_node.next = logic_dict[i][0]
                    cls.__logic_current_node = logic_dict[i][1]
    
    @classmethod
    def display_logic_chain(cls) -> None:
        current_node: Union[logicNode, None] = cls.__logic_head_node
        chain_str = ""
        while current_node is not None:
            data = getattr(current_node, "data", None)
            next_val = "None" if getattr(current_node, "next", None) is None else "node"
            chain_str += f"node{{{data}, {next_val}}} -> "
            current_node = getattr(current_node, "next", None)
        chain_str += "None"
        print(chain_str)

class notNode(logicNode):
    __not_head_node: Optional['notNode'] = None
    __not_current_node: Optional['notNode'] = None

    def __init__(self, data: str, position: int) -> None:
        self.next: Optional['notNode'] = None
        self.data: Dict[str, Any]  = {"position": position, "data": data}

    @classmethod
    def reset_not_head(cls) -> None:
        cls.__not_head_node = None
        cls.__not_current_node = None

    @classmethod
    def get_not_head(cls) -> Union['notNode', None]:
        return cls.__not_head_node

    @classmethod
    def get_not_current(cls) -> Union['notNode', None]:
        return cls.__not_current_node
    
    @classmethod
    def add_new_not_node(cls, new_not_node: 'notNode') -> None:
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