"""Render reconstructed phrase-structure trees as PNG figures."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from parse_candidates import CANDIDATES, task1_candidates
from tree_model import Node


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_font(size: int, bold: bool = False):
    candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\segoeui bold.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def leaf_count(node: Node) -> int:
    return 1 if node.is_leaf() else sum(leaf_count(child) for child in node.children)


def positions(node: Node, x_left: float, x_right: float, depth: int, out: Dict[int, Tuple[float, int]]) -> float:
    if node.is_leaf():
        x = (x_left + x_right) / 2
    else:
        child_widths = [leaf_count(child) for child in node.children]
        total = sum(child_widths)
        cursor = x_left
        child_centers = []
        for width, child in zip(child_widths, node.children):
            next_cursor = cursor + (x_right - x_left) * width / total
            child_centers.append(positions(child, cursor, next_cursor, depth + 1, out))
            cursor = next_cursor
        x = sum(child_centers) / len(child_centers)
    out[id(node)] = (x, depth)
    return x


def render_tree(tree: Node, title: str, output_path: Path) -> None:
    leaves = max(leaf_count(tree), 1)
    canvas_width = max(1300, 150 * leaves)
    canvas_height = max(720, 85 * (tree.depth() + 2))
    image = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(image)
    title_font = load_font(30, bold=True)
    node_font = load_font(22)
    small_font = load_font(18)
    draw.text((30, 20), title, fill=(30, 45, 65), font=title_font)

    node_positions: Dict[int, Tuple[float, int]] = {}
    positions(tree, 70, canvas_width - 70, 0, node_positions)
    y0 = 95
    y_step = 72
    for node in walk(tree):
        x, depth = node_positions[id(node)]
        y = y0 + depth * y_step
        if not node.is_leaf():
            for child in node.children:
                cx, cdepth = node_positions[id(child)]
                cy = y0 + cdepth * y_step
                draw.line((x, y + 18, cx, cy - 18), fill=(125, 140, 155), width=2)
    for node in walk(tree):
        x, depth = node_positions[id(node)]
        y = y0 + depth * y_step
        font = small_font if node.is_leaf() else node_font
        text = node.label
        box = draw.textbbox((0, 0), text, font=font)
        width = box[2] - box[0] + 18
        height = box[3] - box[1] + 10
        fill = (236, 244, 252) if not node.is_leaf() else (250, 250, 250)
        draw.rounded_rectangle((x - width / 2, y - height / 2, x + width / 2, y + height / 2), radius=6, fill=fill, outline=(75, 95, 115), width=2)
        draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2 - 1), text, fill=(20, 30, 40), font=font)
    draw.text((30, canvas_height - 34), "Reconstructed from the classroom slide; not a screenshot.", fill=(100, 100, 100), font=small_font)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def walk(node: Node):
    yield node
    for child in node.children:
        yield from walk(child)


def main() -> None:
    output_dir = PROJECT_ROOT / "figures"
    for candidate_id, tree in CANDIDATES.items():
        render_tree(tree, f"Task 2 candidate ({candidate_id})", output_dir / f"candidate_{candidate_id.lower()}.png")
    task1 = task1_candidates()
    render_tree(task1["B"], "Task 1 classroom choice (B)", output_dir / "task1_b.png")

    overview = Image.new("RGB", (1800, 1180), "white")
    draw = ImageDraw.Draw(overview)
    draw.text((40, 28), "EE6405 Task 2: reconstructed candidate overview", fill=(30, 45, 65), font=load_font(32, bold=True))
    note_font = load_font(22)
    draw.text((40, 78), "CFG validation result: B, C, E", fill=(35, 110, 70), font=note_font)
    thumb_w, thumb_h = 560, 480
    positions_grid = [(40, 140), (620, 140), (1200, 140), (40, 660), (620, 660), (1200, 660)]
    for (candidate_id, _), (x, y) in zip(CANDIDATES.items(), positions_grid):
        path = output_dir / f"candidate_{candidate_id.lower()}.png"
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h))
        overview.paste(thumb, (x, y))
    overview.save(output_dir / "task2_candidates_overview.png")
    print(f"Rendered {len(CANDIDATES)} Task 2 candidate PNGs, Task 1 B, and one overview")


if __name__ == "__main__":
    main()


