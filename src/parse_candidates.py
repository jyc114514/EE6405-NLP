"""Reconstruct the six Task 2 candidate trees from the supplied slide."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from grammar import Grammar, production_counter
from tree_model import Node, c_word, d_word, n_word, np_word, p_word, v_word


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SENTENCE = ("workers", "dumped", "sacks", "of", "garbage", "and", "junk", "into", "a", "bin")


def pp(preposition: str, complement: Node) -> Node:
    return Node("PP", (p_word(preposition), complement))


def np_with_pp(head: str, preposition: str, complement: Node) -> Node:
    return Node("NP", (np_word(head), pp(preposition, complement)))


def cnp(complement: Node) -> Node:
    return Node("CNP", (c_word("and"), complement))


def bin_np() -> Node:
    return Node("NP", (d_word("a"), n_word("bin")))


def sentence(subject: Node, predicate: Node) -> Node:
    return Node("S", (subject, predicate))


def verb_phrase(*children: Node) -> Node:
    return Node("VP", children)


def task2_candidates() -> Dict[str, Node]:
    sacks_of_garbage = np_with_pp("sacks", "of", np_word("garbage"))
    flat_garbage_and_junk = Node(
        "NP", (np_word("garbage"), c_word("and"), np_word("junk"))
    )

    # (a): flat NP coordination occurs inside the of-phrase.
    a_of_np = Node("NP", (np_word("garbage"), c_word("and"), np_word("junk")))
    a_object = Node("NP", (np_with_pp("sacks", "of", a_of_np), pp("into", bin_np())))
    a = sentence(np_word("workers"), verb_phrase(v_word("dumped"), a_object))

    # (b): the coordination is CNP -> C NP, and the into-PP is NP-attached.
    b_coord = Node("NP", (sacks_of_garbage, cnp(np_word("junk"))))
    b_object = Node("NP", (b_coord, pp("into", bin_np())))
    b = sentence(np_word("workers"), verb_phrase(v_word("dumped"), b_object))

    # (c): the into-PP is attached to the right conjunct NP.  It is
    # structurally licensed even though the resulting interpretation is odd.
    c_right = np_with_pp("junk", "into", bin_np())
    c_object = Node("NP", (sacks_of_garbage, cnp(c_right)))
    c = sentence(np_word("workers"), verb_phrase(v_word("dumped"), c_object))

    # (d): the VP has a direct V/NP/PP ternary expansion and the object has
    # flat NP coordination.
    d_flat_object = Node("NP", (sacks_of_garbage, c_word("and"), np_word("junk")))
    d = sentence(
        np_word("workers"),
        verb_phrase(v_word("dumped"), d_flat_object, pp("into", bin_np())),
    )

    # (e): the into-PP is VP-attached; the of-phrase contains a legal CNP.
    e_of_complement = Node("NP", (np_word("garbage"), cnp(np_word("junk"))))
    e_object = Node("NP", (np_word("sacks"), pp("of", e_of_complement)))
    e_inner_vp = verb_phrase(v_word("dumped"), e_object)
    e = sentence(np_word("workers"), verb_phrase(e_inner_vp, pp("into", bin_np())))

    # (f): the of-PP is inside a VP, and its complement uses CNP -> NP C;
    # both are visible structural departures from the minimal CFG.
    f_wrong_cnp = Node("CNP", (np_word("garbage"), c_word("and")))
    f_of_complement = Node("NP", (f_wrong_cnp, np_word("junk")))
    f_inner_vp = verb_phrase(
        verb_phrase(v_word("dumped"), np_word("sacks")),
        pp("of", f_of_complement),
    )
    f = sentence(np_word("workers"), verb_phrase(f_inner_vp, pp("into", bin_np())))

    return {"A": a, "B": b, "C": c, "D": d, "E": e, "F": f}


def task1_candidates() -> Dict[str, Node]:
    she = Node("NP", (Node("PRP", (Node("She"),)),))
    the_lesson = Node("NP", (Node("DT", (Node("the"),)), Node("NN", (Node("lesson"),))))
    to_heart = Node("PP", (Node("IN", (Node("to"),)), Node("NP", (Node("NN", (Node("heart"),)),))))
    a = sentence(she, Node("VP", (Node("VBD", (Node("took"),)), Node("NP", (the_lesson, to_heart)))))
    b = sentence(she, Node("VP", (Node("VBD", (Node("took"),)), the_lesson, to_heart)))
    c_lesson = Node("NP", (Node("DT", (Node("the"),)), Node("NP", (Node("NN", (Node("lesson"),)), to_heart))))
    c = sentence(she, Node("VP", (Node("VBD", (Node("took"),)), c_lesson)))
    d = Node("S", (she, Node("VP", (Node("VBD", (Node("took"),)), the_lesson)), to_heart))
    return {"A": a, "B": b, "C": c, "D": d}


CANDIDATES = task2_candidates()


def main() -> None:
    grammar = Grammar()
    lines = ["Task 2 reconstructed bracket trees", "", f"Expected yield: {' '.join(EXPECTED_SENTENCE)}", ""]
    records = {}
    for candidate_id, tree in CANDIDATES.items():
        lines.append(f"({candidate_id}) {tree.bracket()}")
        lines.append("  productions:")
        for production, count in sorted(production_counter(tree).items()):
            lines.append(f"    {count} x {production}")
        lines.append("")
        records[candidate_id] = {
            "bracket": tree.bracket(),
            "yield": list(tree.yield_tokens()),
            "productions": production_counter(tree),
        }
    output_path = PROJECT_ROOT / "outputs" / "candidate_structures.txt"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    (PROJECT_ROOT / "outputs" / "candidate_structures.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("Reconstructed Task 2 candidates: A, B, C, D, E, F")
    print(f"Candidate structures written to {output_path}")
    print(f"Task 2 yield check: {' '.join(EXPECTED_SENTENCE)}")
    print(f"CFG structural rules available: {len(grammar.structural_rules)}")


if __name__ == "__main__":
    main()


