# Detailed analysis

## 1. Scope and source handling

Source slide used for reconstruction:

```text
D:\NTU学习\专业课学习\6405\课程资料\02\课堂讨论.png
```

The source image is preserved locally as `original_question.png` in the project directory. It is excluded from the GitHub release by `.gitignore`; the public/private repository contains only the reconstruction code, generated figures, logs, and analysis.

The project is deliberately self-contained. It does not import the earlier informal Markdown answer because that answer used a different semantic reading for Task 2. The present project makes the tree transcription and grammar explicit so that the result can be checked and rerun.

## 2. Dependency-versus-constituency mismatch

The slide heading says “Dependency parsing”, but the candidate diagrams are labelled with phrase-structure categories:

- `S` is the sentence root;
- `NP`, `VP`, and `PP` are phrase constituents;
- `CNP` is used for a coordinated noun phrase;
- leaves are words or POS-labelled terminals such as `V`, `P`, `C`, `D`, and `N`.

A dependency tree would normally encode directed head-dependent relations and would not use this bracketed constituent expansion format. Therefore the experiment treats each candidate as a constituency tree and validates local CFG productions. This is a classification of the supplied diagrams, not a claim that the lecture title is correct or incorrect as a whole.

## 3. Reconstructed tree structures

The six Task 2 trees all yield:

```text
workers dumped sacks of garbage and junk into a bin
```

The relevant structural differences are:

| Candidate | Key structure | CFG consequence |
|---|---|---|
| A | `of` complement contains flat `NP -> NP C NP` | invalid |
| B | NP coordination uses `NP -> NP CNP`, with `CNP -> C NP`; `into` is NP-attached | valid |
| C | same legal coordination; `into a bin` is attached inside the right `junk` NP | valid but semantically odd |
| D | direct `VP -> V NP PP` plus flat `NP -> NP C NP` | invalid |
| E | legal `CNP`; `into a bin` is attached by `VP -> VP PP` | valid |
| F | `of` phrase contains reversed/non-licensed coordination (`CNP -> NP C` and `NP -> CNP NP`) | invalid |

The transcriptions are stored in `outputs/candidate_structures.txt` and `.json`, and rendered independently into `figures/candidate_*.png`.

## 4. CFG used by the validator

The minimal structural CFG is:

```text
S    -> NP VP
VP   -> V NP
VP   -> VP PP
NP   -> NP PP
NP   -> NP CNP
CNP  -> C NP
PP   -> P NP
NP   -> D N
```

The lexical rules are the word-level rules needed by the slide:

```text
NP -> workers | sacks | garbage | junk
V  -> dumped
P  -> of | into
C  -> and
D  -> a
N  -> bin
```

The validator is bottom-up and context-free in the operational sense: each node is checked by its own parent label and ordered child labels. It does not inspect the candidate ID. It also checks that every candidate yields the expected token sequence.

The reference answer `(B, C, E)` is used only in a final assertion after `valid_candidates` has already been computed. This prevents the reference list from becoming the classifier.

## 5. Validation evidence

The actual run produced:

```text
Candidate A: INVALID
  NP -> NP C NP is not licensed

Candidate B: VALID

Candidate C: VALID

Candidate D: INVALID
  VP -> V NP PP is not licensed
  NP -> NP C NP is not licensed

Candidate E: VALID

Candidate F: INVALID
  NP -> CNP NP is not licensed
  CNP -> NP C is not licensed

Computed valid candidates: B, C, E
Post-hoc reference check (B,C,E): PASS
```

The full machine-readable report is `outputs/validation_results.json`; the human-readable report is `outputs/validation_results.txt`.

## 6. Generated parses

`generate_valid_parses.py` uses a bounded chart parser over the same grammar and token sequence. It enumerates 10 complete `S` parses under the grammar and compares their canonical bracket forms with the reconstructed candidates. The independent structural match is:

```text
Candidate trees matched by generated parses: B, C, E
```

This second check is useful because it tests the grammar in the generative direction rather than only testing each candidate in the recognition direction.

## 7. Task 1: why B is the classroom choice

Task 1 is treated separately because the slide's four trees are a short classroom interpretation of the idiom “take something to heart”, not the Task 2 CFG benchmark.

- **B** keeps `the lesson` as the object NP and places `to heart` at VP level, matching the intended idiomatic predicate structure.
- **A** puts `to heart` inside the object NP, as if it modified `lesson`.
- **C** embeds the PP even more deeply inside the noun phrase headed by `lesson`.
- **D** makes `to heart` a sibling of the VP directly under `S`, which does not match the normal sentence constituent structure.

The image is therefore best described as a constituency-tree teaching question whose expected Task 1 choice is B, despite the dependency-parsing title.

## 8. Syntax versus semantics

The formal result is intentionally not a “sounds natural” ranking.

Candidate C is the important counterexample: its tree is generated by the CFG, but the PP attachment makes `junk into a bin` an unusual interpretation. Candidate D illustrates the reverse situation: a listener may infer a sensible dumping event, but the exact tree drawn in the slide is not generated by the minimal grammar. A constituency grammar validates structure; it does not by itself encode selectional preferences, idiomaticity, or world knowledge.

## 9. Environment and reproducibility

`outputs/run_log.txt` records the full run. In the current Windows environment:

```text
requested_environment: ai_env
ai_env_active: False
conda_on_PATH: (not found)
python_on_PATH: (not found)
python_executable_used: bundled workspace Python runtime
```

The fallback uses the bundled Python runtime and Pillow only for image rendering. No system packages were installed, and no external NLP model or parser was invoked.

Run from the project root with:

```powershell
python src/run_all.py
```

The runner executes candidate reconstruction, bottom-up validation, bounded parse generation, and tree rendering in that order. It captures each child process's stdout, stderr, and exit code into `outputs/run_log.txt`.


