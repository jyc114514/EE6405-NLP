"""Bottom-up validation of the six reconstructed Task 2 trees."""

from __future__ import annotations

import json
from pathlib import Path

from grammar import Grammar
from parse_candidates import CANDIDATES, EXPECTED_SENTENCE


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_VALID = ("B", "C", "E")


def main() -> None:
    grammar = Grammar()
    records = []
    valid_candidates = []
    for candidate_id, tree in CANDIDATES.items():
        errors = grammar.validate_tree(tree, EXPECTED_SENTENCE)
        valid = not errors
        if valid:
            valid_candidates.append(candidate_id)
        records.append(
            {
                "candidate": candidate_id,
                "valid": valid,
                "yield": list(tree.yield_tokens()),
                "errors": errors,
                "bracket": tree.bracket(),
            }
        )

    result = {
        "grammar": {
            "structural_rules": [f"{parent} -> {' '.join(children)}" for parent, children in grammar.structural_rules],
            "lexical_rules": [f"{parent} -> {' '.join(children)}" for parent, children in grammar.lexical_rules],
        },
        "candidates": records,
        "computed_valid_candidates": valid_candidates,
        "reference_check": {
            "reference_valid_candidates": list(REFERENCE_VALID),
            "matches_reference": tuple(valid_candidates) == REFERENCE_VALID,
            "note": "The reference list is checked only after bottom-up validation; it is not used as a classifier.",
        },
    }
    json_path = PROJECT_ROOT / "outputs" / "validation_results.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    text_lines = [
        "EE6405 Task 2 bottom-up CFG validation",
        "========================================",
        "",
        grammar.rule_text().rstrip(),
        "",
    ]
    for record in records:
        text_lines.append(f"Candidate {record['candidate']}: {'VALID' if record['valid'] else 'INVALID'}")
        if record["errors"]:
            for error in record["errors"]:
                text_lines.append(f"  - {error['path']}: {error['production']} ({error['reason']})")
        else:
            text_lines.append("  - no grammar or yield errors")
        text_lines.append("")
    text_lines.extend(
        [
            f"Computed valid candidates: {', '.join(valid_candidates)}",
            f"Post-hoc reference check (B,C,E): {'PASS' if tuple(valid_candidates) == REFERENCE_VALID else 'FAIL'}",
        ]
    )
    text_path = PROJECT_ROOT / "outputs" / "validation_results.txt"
    text_path.write_text("\n".join(text_lines) + "\n", encoding="utf-8")

    print("Computed valid candidates:", ", ".join(valid_candidates))
    print(f"Validation results written to {text_path}")
    print(f"Post-hoc reference check (B,C,E): {'PASS' if tuple(valid_candidates) == REFERENCE_VALID else 'FAIL'}")

    # This is an assertion on the independently computed result, not the
    # mechanism that decides whether an individual tree is valid.
    assert tuple(valid_candidates) == REFERENCE_VALID, valid_candidates


if __name__ == "__main__":
    main()


