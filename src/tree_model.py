"""Small immutable tree model used by the EE6405 parsing experiment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Tuple


@dataclass(frozen=True)
class Node:
    """A phrase-structure node.

    Leaves are represented as nodes with no children.  This keeps the source
    trees close to the labels visible in the classroom slide: for example,
    ``(NP workers)`` and ``(V dumped)``.
    """

    label: str
    children: Tuple["Node", ...] = ()

    def __init__(self, label: str, children: Iterable["Node"] = ()):
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "children", tuple(children))

    def is_leaf(self) -> bool:
        return not self.children

    def bracket(self) -> str:
        if self.is_leaf():
            return self.label
        return "(" + self.label + " " + " ".join(child.bracket() for child in self.children) + ")"

    def yield_tokens(self) -> Tuple[str, ...]:
        if self.is_leaf():
            return (self.label,)
        tokens = []
        for child in self.children:
            tokens.extend(child.yield_tokens())
        return tuple(tokens)

    def productions(self) -> Iterator[Tuple[str, Tuple[str, ...]]]:
        """Yield every local production, including lexical productions."""
        if self.children:
            yield self.label, tuple(child.label for child in self.children)
            for child in self.children:
                yield from child.productions()

    def depth(self) -> int:
        if self.is_leaf():
            return 0
        return 1 + max(child.depth() for child in self.children)


def leaf(token: str) -> Node:
    return Node(token)


def lexical(label: str, token: str) -> Node:
    return Node(label, (leaf(token),))


def np_word(token: str) -> Node:
    return lexical("NP", token)


def v_word(token: str) -> Node:
    return lexical("V", token)


def p_word(token: str) -> Node:
    return lexical("P", token)


def c_word(token: str) -> Node:
    return lexical("C", token)


def d_word(token: str) -> Node:
    return lexical("D", token)


def n_word(token: str) -> Node:
    return lexical("N", token)


