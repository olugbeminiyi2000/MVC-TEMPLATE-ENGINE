from __future__ import annotations
from typing import Optional, Any, Union

class IterableLinkedList:
    __iterable_head_node: Optional['IterableLinkedList'] = None
    __iterable_current_node: Optional['IterableLinkedList'] = None

    def __init__(self, data: str) -> None:
        self.data: Any = data
        self.next: Optional['IterableLinkedList'] = None

    @classmethod
    def reset_iterable_head(cls) -> None:
        cls.__iterable_head_node = None
        cls.__iterable_current_node = None

    @classmethod
    def get_iterable_head(cls) -> Union['IterableLinkedList', None]:
        return cls.__iterable_head_node
    
    @classmethod
    def add_new_iterable_node(cls, new_iterable_node: 'IterableLinkedList') -> None:
        iterable_head_node: Union['IterableLinkedList', None] = cls.__iterable_head_node
        if not iterable_head_node:
            cls.__iterable_head_node = new_iterable_node
            cls.__iterable_current_node = new_iterable_node
        else:
            current_iterable_node: 'IterableLinkedList' = cls.__iterable_current_node
            current_iterable_node.next = new_iterable_node
            cls.__iterable_current_node = new_iterable_node
    
    @classmethod
    def display_iterable_chain(cls) -> None:
        """Print a string representation of the current logic chain for debugging."""
        node_cursor: Union[IterableLinkedList, None] = cls.__iterable_head_node
        chain_repr = ""
        while node_cursor is not None:
            node_data = getattr(node_cursor, "data", None)
            next_node_repr = "None" if getattr(node_cursor, "next", None) is None else "node"
            chain_repr += f"node{{{node_data}, {next_node_repr}}} -> "
            node_cursor = getattr(node_cursor, "next", None)
        chain_repr += "None"