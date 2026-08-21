"""Enumerate bounded parses for the Task 2 token sequence under the CFG."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, Iterator, List, Sequence, Tuple

from grammar import Grammar
from parse_candidates import CANDIDATES, EXPECTED_SENTENCE
from tree_model import Node


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_TREES_PER_CELL = 500


def partitions(start: int, end: int, parts: int) -> Iterator[Tuple[Tuple[int, int], ...]]:
    if parts == 1:
        yield ((start, end),)
        return
    for cut in range(start + 1, end):
        for rest in partitions(cut, end, parts - 1):
            yield ((start, cut),) + rest


def bounded_unique_append(bucket: List[Node], tree: Node) -> None:
    key = tree.bracket()
    if any(existing.bracket() == key for existing in bucket):
        return
    if len(bucket) < MAX_TREES_PER_CELL:
        bucket.append(tree)


def parse_tokens(tokens: Sequence[str], grammar: Grammar) -> List[Node]:
    chart: DefaultDict[Tuple[str, int, int], List[Node]] = defaultdict(list)

    for index, token in enumerate(tokens):
        for label, rhs in grammar.lexical_rules:
            if rhs == (token,):
                chart[(label, index, index + 1)].append(Node(label, (Node(token),)))

    # There are no epsilon or unary rules in this grammar, so each span can
    # be completed once its shorter child spans have been completed.
    for span_length in range(2, len(tokens) + 1):
        for start in range(0, len(tokens) - span_length + 1):
            end = start + span_length
            for parent, rhs in grammar.structural_rules:
                for spans in partitions(start, end, len(rhs)):
                    child_options: List[List[Node]] = []
                    if any(not chart[(symbol, left, right)] for symbol, (left, right) in zip(rhs, spans)):
                        continue
                    child_options = [chart[(symbol, left, right)] for symbol, (left, right) in zip(rhs, spans)]
                    combinations: List[Tuple[Node, ...]] = [()]
                    for options in child_options:
                        combinations = [prefix + (child,) for prefix in combinations for child in options]
                    for children in combinations:
                        bounded_unique_append(chart[(parent, start, end)], Node(parent, children))

    return chart[("S", 0, len(tokens))]


def main() -> None:
    grammar = Grammar()
    parses = parse_tokens(EXPECTED_SENTENCE, grammar)
    parse_keys = {tree.bracket() for tree in parses}
    matching_candidates = [
        candidate_id
        for candidate_id, tree in CANDIDATES.items()
        if tree.bracket() in parse_keys
    ]

    lines = [
        "Bounded CFG parse generation for Task 2",
        "========================================",
        f"Tokens: {' '.join(EXPECTED_SENTENCE)}",
        f"Maximum trees per chart cell: {MAX_TREES_PER_CELL}",
        f"Generated complete S parses: {len(parses)}",
        f"Candidate trees matched by generated parses: {', '.join(matching_candidates) or '(none)'}",
        "",
        "Generated bracket trees:",
    ]
    for index, tree in enumerate(parses, 1):
        lines.append(f"{index:03d}. {tree.bracket()}")
    output_path = PROJECT_ROOT / "outputs" / "generated_parses.txt"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated complete S parses: {len(parses)}")
    print("Candidate trees matched by generated parses:", ", ".join(matching_candidates) or "(none)")
    print(f"Generated parses written to {output_path}")


if __name__ == "__main__":
    main()


