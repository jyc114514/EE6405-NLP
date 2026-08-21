"""The minimal phrase-structure grammar used in the EE6405 experiment.

The slide is labelled "Dependency parsing", but the supplied trees are
constituency trees.  The grammar therefore checks local phrase-structure
productions rather than dependency heads and arcs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from tree_model import Node


Production = Tuple[str, Tuple[str, ...]]


STRUCTURAL_RULES: Tuple[Production, ...] = (
    ("S", ("NP", "VP")),
    ("VP", ("V", "NP")),
    ("VP", ("VP", "PP")),
    ("NP", ("NP", "PP")),
    ("NP", ("NP", "CNP")),
    ("CNP", ("C", "NP")),
    ("PP", ("P", "NP")),
    ("NP", ("D", "N")),
)


LEXICAL_RULES: Tuple[Production, ...] = (
    ("NP", ("workers",)),
    ("NP", ("sacks",)),
    ("NP", ("garbage",)),
    ("NP", ("junk",)),
    ("V", ("dumped",)),
    ("P", ("of",)),
    ("P", ("into",)),
    ("C", ("and",)),
    ("D", ("a",)),
    ("N", ("bin",)),
)


@dataclass(frozen=True)
class Grammar:
    """A finite CFG with exact-arity productions."""

    structural_rules: Tuple[Production, ...] = STRUCTURAL_RULES
    lexical_rules: Tuple[Production, ...] = LEXICAL_RULES

    @property
    def rules(self) -> Tuple[Production, ...]:
        return self.structural_rules + self.lexical_rules

    def allows(self, parent: str, children: Sequence[str]) -> bool:
        return (parent, tuple(children)) in self.rules

    def rule_text(self) -> str:
        lines = ["Structural rules:"]
        lines.extend(format_production(rule) for rule in self.structural_rules)
        lines.append("")
        lines.append("Lexical rules:")
        lines.extend(format_production(rule) for rule in self.lexical_rules)
        return "\n".join(lines) + "\n"

    def validate_node(self, node: Node, path: str = "ROOT") -> List[Dict[str, object]]:
        """Return bottom-up validation errors for one tree.

        This is deliberately local and structural: no candidate ID is used,
        and no semantic plausibility judgment is used as a grammar rule.
        """
        errors: List[Dict[str, object]] = []
        child_labels = tuple(child.label for child in node.children)
        if node.children and not self.allows(node.label, child_labels):
            errors.append(
                {
                    "path": path,
                    "production": format_production((node.label, child_labels)),
                    "reason": "production is not licensed by the grammar",
                }
            )
        for index, child in enumerate(node.children):
            errors.extend(self.validate_node(child, f"{path}/{node.label}[{index}]") )
        return errors

    def validate_tree(self, root: Node, expected_tokens: Iterable[str]) -> List[Dict[str, object]]:
        errors = self.validate_node(root)
        actual = root.yield_tokens()
        expected = tuple(expected_tokens)
        if actual != expected:
            errors.append(
                {
                    "path": "ROOT",
                    "production": "yield",
                    "reason": f"yield mismatch: expected {expected}, got {actual}",
                }
            )
        return errors


def format_production(production: Production) -> str:
    parent, children = production
    return f"{parent} -> {' '.join(children)}"


def production_counter(node: Node) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for parent, children in node.productions():
        key = format_production((parent, children))
        counts[key] = counts.get(key, 0) + 1
    return counts


