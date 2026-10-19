#!/usr/bin/env python3
"""Read-only static audit and presentation-only change guard for the questbook."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess
import sys

import ftb_snbt_lib as snbt


BASELINE = "f68124fb33597aa13b4b6a8dd8c6dde7c879b188"
REFERENCE = "nasledie_defense"
QUEST_ROOT = "config/ftbquests/quests/"
CHAPTER_ROOT = QUEST_ROOT + "chapters/"
PRESENTATION = {"title", "description", "icon", "x", "y", "shape", "size"}
INPUT_ROOTS = (QUEST_ROOT.rstrip("/"), "kubejs")
LONG_EDGE = 8.0
EPSILON = 1e-8
TECHNICAL_PROSE = {
    "autocheck": r"авто(?:проверка|зач[её]т)|автоматическ\w*\s+проверк",
    "implementation": r"\b(?:Item\s+Task|Task\s+ID|Quest\s+ID|Reward\s+ID|advancement|FTB\s+Quests|KubeJS|SNBT|NBT)\b",
    "resource_id": r"\b[a-z][a-z0-9_]*:[a-z0-9_]+(?:/[a-z0-9_]+)*\b",
    "template_label": r"(?:^|\n)\s*(?:Зачем|Практика|Техническая проверка)\s*:",
}


def canonical(value):
    """Preserve SNBT numeric types as well as values in protected fields."""
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [canonical(v) for v in value]
    if isinstance(value, (int, float)):
        return {"$number_type": type(value).__name__, "$value": float(value) if isinstance(value, float) else int(value)}
    return str(value) if isinstance(value, str) else value


def digest(value):
    return hashlib.sha256(json.dumps(canonical(value), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def problem(code, location, message, **details):
    return {"code": code, "location": location, "message": message, **details}


def parse_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique)


def parse_files(files):
    parsed, errors = {}, []
    for name, content in sorted(files.items()):
        if name.endswith((".snbt", ".json")):
            try:
                parser = snbt.loads if name.endswith(".snbt") else parse_json
                parsed[name] = parser(content.decode("utf-8"))
            except (ValueError, TypeError, UnicodeError, KeyError, IndexError) as exc:
                errors.append(problem("parse", name, str(exc)))
    return parsed, errors


def chapters(parsed):
    return {name: body for name, body in parsed.items() if name.startswith(CHAPTER_ROOT) and name.endswith(".snbt")}


def quest_rows(parsed):
    for name, chapter in chapters(parsed).items():
        for quest in chapter.get("quests", []):
            yield name, chapter, quest


def inventory(parsed):
    rows = list(quest_rows(parsed))
    return {
        "chapters": len(chapters(parsed)), "quests": len(rows),
        "tasks": sum(len(q.get("tasks", [])) for _, _, q in rows),
        "rewards": sum(len(q.get("rewards", [])) for _, _, q in rows),
        "dependencies": sum(len(q.get("dependencies", [])) for _, _, q in rows),
        "optional_quests": sum(bool(q.get("optional", False)) for _, _, q in rows),
        "task_types": dict(sorted(Counter(str(t.get("type")) for _, _, q in rows for t in q.get("tasks", [])).items())),
        "reward_types": dict(sorted(Counter(str(r.get("type")) for _, _, q in rows for r in q.get("rewards", [])).items())),
        "parsed_json": sum(n.endswith(".json") for n in parsed),
        "parsed_snbt": sum(n.endswith(".snbt") for n in parsed),
    }


def entities(parsed):
    for name, chapter in chapters(parsed).items():
        yield "chapter", name, chapter
        for quest in chapter.get("quests", []):
            yield "quest", f"{name}#{quest.get('id', '?')}", quest
            for category in ("tasks", "rewards"):
                for child in quest.get(category, []):
                    yield category[:-1], f"{name}#{quest.get('id', '?')}/{category}/{child.get('id', '?')}", child
    group_file = QUEST_ROOT + "chapter_groups.snbt"
    for group in parsed.get(group_file, {}).get("chapter_groups", []):
        yield "group", group_file, group


def integrity(parsed):
    errors, seen = [], {}
    for category, location, entity in entities(parsed):
        ident = str(entity.get("id", ""))
        if not re.fullmatch(r"[0-9A-Fa-f]{16}", ident):
            errors.append(problem("id_format", location, "Missing or malformed 16-digit hexadecimal ID", id=ident, category=category))
        # Hexadecimal case must not create two identities for the same number.
        key = ident.upper()
        if key in seen:
            errors.append(problem("id_duplicate", location, "ID is not globally unique", id=ident, previous=seen[key]))
        seen[key] = location
    quests = {str(q.get("id")): q for _, _, q in quest_rows(parsed)}
    graph = {}
    for name, _, q in quest_rows(parsed):
        ident, deps = str(q.get("id")), [str(d) for d in q.get("dependencies", [])]
        location = f"{name}#{ident}"
        for dep in deps:
            if dep not in quests:
                errors.append(problem("dependency_missing", location, "Dependency does not resolve to a quest", dependency=dep))
            if dep == ident:
                errors.append(problem("dependency_self", location, "Quest depends on itself"))
        if len(deps) != len(set(deps)):
            errors.append(problem("dependency_duplicate", location, "Dependency appears more than once"))
        graph[ident] = [d for d in deps if d in quests]
    # Iterative Kahn traversal avoids recursion limits on future large chapters.
    remaining = {ident: len(set(deps)) for ident, deps in graph.items()}
    dependents = defaultdict(list)
    for ident, deps in graph.items():
        for dep in set(deps):
            dependents[dep].append(ident)
    ready = [ident for ident, count in remaining.items() if count == 0]
    while ready:
        ident = ready.pop()
        for dependent in dependents[ident]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                ready.append(dependent)
    blocked = sorted(k for k, v in remaining.items() if v)
    if blocked:
        errors.append(problem("dependency_cycle", QUEST_ROOT, "Dependency cycle exists; listed quests include any downstream blocked quests", blocked_quests=blocked))
    group_ids = {str(e.get("id")) for category, _, e in entities(parsed) if category == "group"}
    for name, chapter in chapters(parsed).items():
        if chapter.get("group") and str(chapter["group"]) not in group_ids:
            errors.append(problem("chapter_group_missing", name, "Chapter group does not exist", group=str(chapter["group"])))
    return errors


def protected_body(chapter):
    result = {key: value for key, value in chapter.items() if key not in PRESENTATION and key != "quests"}
    result["quests"] = [{key: value for key, value in q.items() if key not in PRESENTATION} for q in chapter.get("quests", [])]
    return result


def preservation(current_files, baseline_files, current, baseline, reference):
    errors, changes = [], []
    reference_file = CHAPTER_ROOT + reference + ".snbt"
    if reference_file not in current or reference_file not in baseline:
        errors.append(problem("reference_missing", reference_file, "Reference chapter must exist in both snapshots"))
    for name in sorted(set(current_files) | set(baseline_files)):
        old, new = baseline_files.get(name), current_files.get(name)
        if old == new:
            continue
        changes.append({"file": name, "baseline_sha256": hashlib.sha256(old).hexdigest() if old is not None else None,
                        "current_sha256": hashlib.sha256(new).hexdigest() if new is not None else None})
        if name != reference_file:
            errors.append(problem("protected_file_changed", name, "Only the selected chapter's presentation may change in this stage"))
    if reference_file in current and reference_file in baseline:
        old, new = baseline[reference_file], current[reference_file]
        if canonical(protected_body(old)) != canonical(protected_body(new)):
            errors.append(problem("mechanics_changed", reference_file,
                                  "A protected field changed: IDs, tasks, rewards, dependencies, optional flags, chapter settings and quest order are immutable"))
        old_quests = {str(q.get("id")): q for q in old.get("quests", [])}
        for quest in new.get("quests", []):
            ident = str(quest.get("id"))
            previous = old_quests.get(ident)
            if previous:
                for key in sorted((set(previous) | set(quest)) - PRESENTATION):
                    if canonical(previous.get(key)) != canonical(quest.get(key)) or (key in previous) != (key in quest):
                        errors.append(problem("protected_quest_field", f"{reference_file}#{ident}", f"Protected field changed: {key}", field=key))
    before = Counter((kind, str(e.get("id"))) for kind, _, e in entities(baseline))
    after = Counter((kind, str(e.get("id"))) for kind, _, e in entities(current))
    if before != after:
        errors.append(problem("id_inventory_changed", QUEST_ROOT, "Entity IDs or their categories were added, removed or reused",
                              removed=[list(key) for key in (before - after).elements()], added=[list(key) for key in (after - before).elements()]))
    return errors, changes


def prose_issues(parsed):
    result = []
    for kind, location, entity in entities(parsed):
        if kind not in ("quest", "chapter"):
            continue
        description = entity.get("description", [])
        if isinstance(description, str):
            description = [description]
        text = "\n".join([str(entity.get("title", "")), *map(str, description)])
        text = re.sub(r"§.", "", text)
        matches = [name for name, pattern in TECHNICAL_PROSE.items() if re.search(pattern, text, re.I)]
        if matches:
            result.append(problem("technical_prose", location, "Player-facing text contains implementation details or template labels", patterns=matches))
    return result


def distance_to_segment(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    norm = dx * dx + dy * dy
    if norm < EPSILON:
        return math.dist(point, a)
    position = max(0.0, min(1.0, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / norm))
    return math.dist(point, (a[0] + position * dx, a[1] + position * dy))


def segment_crossing(a, b, c, d):
    def cross(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    x1, x2, x3, x4 = cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)
    if x1 * x2 < -EPSILON and x3 * x4 < -EPSILON:
        return "crossing"
    if all(abs(x) < EPSILON for x in (x1, x2, x3, x4)):
        axis = 0 if abs(a[0] - b[0]) >= abs(a[1] - b[1]) else 1
        overlap = min(max(a[axis], b[axis]), max(c[axis], d[axis])) - max(min(a[axis], b[axis]), min(c[axis], d[axis]))
        if overlap > EPSILON:
            return "collinear_overlap"
    return None


def geometry(parsed):
    issues, metrics = [], {}
    for name, chapter in chapters(parsed).items():
        positions, radii = {}, {}
        quests = {str(q.get("id")): q for q in chapter.get("quests", [])}
        for ident, q in quests.items():
            try:
                x, y, size = float(q.get("x", 0)), float(q.get("y", 0)), float(q.get("size", 1))
                if not all(map(math.isfinite, (x, y, size))) or size <= 0:
                    raise ValueError("Coordinates must be finite and size positive")
                positions[ident], radii[ident] = (x, y), size / 2
            except (ValueError, TypeError) as exc:
                issues.append(problem("node_geometry_invalid", f"{name}#{ident}", str(exc)))
        for first, second in itertools.combinations(sorted(positions), 2):
            penetration = radii[first] + radii[second] - math.dist(positions[first], positions[second])
            if penetration > EPSILON:
                issues.append(problem("node_overlap", name, "Quest node disks overlap", nodes=[first, second], magnitude=round(penetration, 6)))
        edges = []
        for ident, q in quests.items():
            if ident not in positions:
                continue
            for dep in q.get("dependencies", []):
                dep = str(dep)
                if dep in positions and dep != ident:
                    edges.append((dep, ident))
        lengths = []
        for first, second in edges:
            a, b = positions[first], positions[second]
            length = math.dist(a, b)
            lengths.append(length)
            if length > LONG_EDGE:
                issues.append(problem("edge_long", name, "Dependency edge exceeds the review threshold", edge=[first, second], magnitude=round(length, 6), threshold=LONG_EDGE))
            for ident, pos in positions.items():
                if ident in (first, second):
                    continue
                penetration = radii[ident] - distance_to_segment(pos, a, b)
                if penetration > EPSILON:
                    issues.append(problem("edge_through_node", name, "Dependency line passes through an unrelated node disk", edge=[first, second], node=ident, magnitude=round(penetration, 6)))
        for first, second in itertools.combinations(edges, 2):
            # Shared endpoints are expected; overlap along a shared ray is still ambiguous.
            crossing = segment_crossing(positions[first[0]], positions[first[1]], positions[second[0]], positions[second[1]])
            if crossing and (not set(first).intersection(second) or crossing == "collinear_overlap"):
                issues.append(problem("edge_crossing", name, "Dependency lines intersect or overlap", edges=sorted([list(first), list(second)]), crossing=crossing))
        xs, ys = [p[0] for p in positions.values()], [p[1] for p in positions.values()]
        metrics[name] = {"nodes": len(positions), "edges": len(edges), "max_edge_length": round(max(lengths, default=0), 4),
                         "width": round(max(xs) - min(xs), 4) if xs else 0, "height": round(max(ys) - min(ys), 4) if ys else 0}
    return issues, metrics


def local_advancement(identifier, parsed):
    if not isinstance(identifier, str) or ":" not in identifier:
        return None
    namespace, path = identifier.split(":", 1)
    return parsed.get(f"kubejs/data/{namespace}/advancements/{path}.json")


def duplicate_conditions(parsed):
    grouped = defaultdict(list)
    for name, _, quest in quest_rows(parsed):
        for task in quest.get("tasks", []):
            condition = {k: v for k, v in task.items() if k not in ("id", "title")}
            if task.get("type") == "advancement":
                advancement = local_advancement(task.get("advancement"), parsed)
                if advancement is not None:
                    condition["advancement"] = {k: v for k, v in advancement.items() if k in ("criteria", "requirements")}
            grouped[digest(condition)].append({"quest": str(quest.get("id")), "task": str(task.get("id")), "file": name})
    return [problem("duplicate_condition", QUEST_ROOT, "Tasks have identical normalized conditions; review whether one action credits unrelated quests", tasks=tasks)
            for tasks in grouped.values() if len(tasks) > 1]


def resource_checks(files, parsed):
    errors = []
    local_namespaces = {name.split("/")[2] for name in files if name.startswith("kubejs/data/") and len(name.split("/")) > 3}
    for name, _, quest in quest_rows(parsed):
        for task in quest.get("tasks", []):
            if task.get("type") == "advancement":
                identifier = str(task.get("advancement", ""))
                if identifier.split(":", 1)[0] in local_namespaces and local_advancement(identifier, parsed) is None:
                    errors.append(problem("local_advancement_missing", f"{name}#{quest.get('id')}", "Local advancement task cannot resolve its resource", resource=identifier))
    for name, body in parsed.items():
        if "/advancements/" not in name or not name.startswith("kubejs/data/"):
            continue
        criteria = body.get("criteria", {})
        if not isinstance(criteria, dict) or not criteria:
            errors.append(problem("advancement_criteria", name, "Advancement needs a nonempty criteria object"))
            continue
        for key, criterion in criteria.items():
            if not isinstance(criterion, dict) or not criterion.get("trigger"):
                errors.append(problem("advancement_trigger", name, "Criterion is missing its trigger", criterion=key))
        requirements = body.get("requirements")
        if requirements is not None:
            if not isinstance(requirements, list) or not requirements or any(not isinstance(group, list) or not group for group in requirements):
                errors.append(problem("advancement_requirements", name, "Requirements must contain nonempty OR groups"))
            else:
                referenced = {str(key) for group in requirements for key in group}
                if referenced != set(criteria):
                    errors.append(problem("advancement_requirements", name, "Requirement names do not exactly cover criterion names", missing=sorted(set(criteria) - referenced), unknown=sorted(referenced - set(criteria))))
        parent = body.get("parent")
        if parent and str(parent).split(":", 1)[0] in local_namespaces and local_advancement(parent, parsed) is None:
            errors.append(problem("local_advancement_parent_missing", name, "Local parent advancement is missing", resource=str(parent)))
    theme_name = "kubejs/assets/ftbquests/ftb_quests_theme.txt"
    theme = files.get(theme_name, b"").decode("utf-8")
    extra = re.search(r"(?m)^extra_quest_shapes:\s*(.*)$", theme)
    custom_shapes = [s.strip() for s in extra.group(1).split(",")] if extra else []
    for shape in custom_shapes:
        for texture in ("shape", "outline", "background"):
            name = f"kubejs/assets/ftbquests/textures/shapes/{shape}/{texture}.png"
            if name not in files:
                errors.append(problem("shape_texture_missing", name, "Declared custom quest shape has a missing texture"))
    return errors


def issue_key(issue):
    return json.dumps({k: v for k, v in issue.items() if k not in ("message", "magnitude")}, sort_keys=True, ensure_ascii=False)


def classify_quality(current, baseline, reference):
    previous = {issue_key(i): i for i in baseline}
    errors, warnings = [], []
    reference_file = CHAPTER_ROOT + reference + ".snbt"
    for issue in current:
        old = previous.get(issue_key(issue))
        touches_reference = issue["location"].startswith(reference_file) or any(t.get("file") == reference_file for t in issue.get("tasks", []))
        worse = old is None or issue.get("magnitude", 0) > old.get("magnitude", 0) + EPSILON
        item = {**issue, "baseline_status": "new_or_worsened" if worse else "pre_existing"}
        if issue["code"] == "node_geometry_invalid" or (touches_reference and worse):
            errors.append(item)
        else:
            warnings.append(item)
    return errors, warnings


def resource_ids(parsed):
    result = defaultdict(set)
    for _, chapter in chapters(parsed).items():
        icon = chapter.get("icon")
        if isinstance(icon, str) and re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", icon):
            result["items"].add(str(icon))
    for _, _, quest in quest_rows(parsed):
        icon = quest.get("icon")
        if isinstance(icon, str) and re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", icon):
            result["items"].add(str(icon))
        for entry in [*quest.get("tasks", []), *quest.get("rewards", [])]:
            for field, category in (("advancement", "advancements"), ("biome", "biomes"), ("entity", "entities"), ("structure", "structures"), ("dimension", "dimensions")):
                if entry.get(field):
                    result[category].add(str(entry[field]))
            item = entry.get("item")
            if isinstance(item, dict) and item.get("id"):
                result["items"].add(str(item["id"]))
            elif isinstance(item, str):
                result["items"].add(str(item))
    return result


def registry_checks(parsed, registry):
    required = resource_ids(parsed)
    local = {ident for ident in required["advancements"] if local_advancement(ident, parsed) is not None}
    required["advancements"] -= local
    summary = {"local_advancements_resolved": len(local), "source": None, "categories": {}}
    unknown, errors = [], []
    evidence = registry.get("evidence", {}) if isinstance(registry, dict) else {}
    evidenced = isinstance(evidence, dict) and isinstance(evidence.get("source"), str) and bool(evidence["source"]) and bool(re.fullmatch(r"[a-fA-F0-9]{64}", str(evidence.get("sha256", ""))))
    if evidenced:
        summary["source"] = evidence
    elif registry is not None:
        errors.append(problem("registry_evidence_missing", "registry", "Registry must identify its actual source and source SHA256; model/texture filenames are not a runtime item registry"))
    for category, identifiers in sorted(required.items()):
        supplied = registry.get(category) if evidenced else None
        if not isinstance(supplied, list):
            summary["categories"][category] = {"required": len(identifiers), "status": "unknown", "unverified": sorted(identifiers)}
            if identifiers:
                unknown.append(problem("external_registry_unknown", category, "Exact registry/data evidence was not supplied; identifier validity is not established", count=len(identifiers)))
            continue
        if not all(isinstance(x, str) for x in supplied):
            errors.append(problem("registry_format", category, "Registry values must be strings"))
            continue
        missing = sorted(identifiers - set(supplied))
        summary["categories"][category] = {"required": len(identifiers), "status": "checked_against_supplied_evidence", "missing": missing}
        for identifier in missing:
            errors.append(problem("external_resource_missing", category, "Identifier is absent from the supplied registry snapshot", resource=identifier))
    return errors, unknown, summary


def semantic_coverage(reviews, baseline, baseline_commit):
    expected = {str(q.get("id")) for _, _, q in quest_rows(baseline)}
    covered, errors, unknown = set(), [], []
    files = []
    for name, review in sorted(reviews.items()):
        files.append(name)
        if review.get("baseline_commit") != baseline_commit:
            errors.append(problem("semantic_baseline", name, "Semantic review does not identify the selected baseline commit"))
            continue
        for entry in review.get("quests", []):
            ident = str(entry.get("id", ""))
            if ident not in expected:
                errors.append(problem("semantic_unknown_id", name, "Semantic review names an unknown baseline quest", id=ident))
            elif ident in covered:
                errors.append(problem("semantic_duplicate", name, "Quest occurs in more than one baseline semantic review", id=ident))
            else:
                covered.add(ident)
    missing = sorted(expected - covered)
    if missing:
        unknown.append(problem("semantic_coverage_incomplete", "reviews/semantic_*.json", "Baseline quests still lack recorded editorial review", count=len(missing)))
    return errors, unknown, {"files": files, "covered": len(covered), "total": len(expected), "unreviewed": missing,
                             "meaning": "Coverage records human/agent editorial review; it does not prove gameplay correctness or validate changed text."}


def introduced_icons(current, baseline, evidence):
    """New icons need retained registration/model evidence, not a guess from their name."""
    before = {str(q.get('id')): q for _, _, q in quest_rows(baseline)}
    supported = (evidence or {}).get('items', {})
    errors = []
    for name, _, quest in quest_rows(current):
        old = before.get(str(quest.get('id')), {})
        icon = str(quest.get('icon', ''))
        if icon == str(old.get('icon', '')):
            continue
        entry = supported.get(icon, {})
        if not (entry.get('kind') in ('minecraft_builtin', 'forge_item_registration')
                and re.fullmatch('[a-f0-9]{64}', str(entry.get('source_sha256', '')))
                and entry.get('registration_evidence') and entry.get('model')
                and re.fullmatch('[a-f0-9]{64}', str(entry.get('model_sha256', '')))
                and entry.get('textures')):
            errors.append(problem('new_icon_unverified', f'{name}#{quest.get("id")}',
                                  'New icon lacks exact-version registration/model/texture evidence', icon=icon))
    return errors


def evaluate(current_files, baseline_files, reference=REFERENCE, registry=None, reviews=None, baseline_commit=BASELINE, icon_evidence=None):
    current, parse_errors = parse_files(current_files)
    baseline, baseline_errors = parse_files(baseline_files)
    report = {"schema_version": 1, "baseline_commit": baseline_commit, "reference": reference,
              "scope": "Static checks only; no Minecraft client/server gameplay test.",
              "errors": parse_errors + [{**e, "location": "baseline:" + e["location"]} for e in baseline_errors], "warnings": [], "unknown": []}
    if report["errors"]:
        return finish(report)
    report["counts"], report["baseline_counts"] = inventory(current), inventory(baseline)
    report["errors"].extend(integrity(current))
    preservation_errors, report["changed_files"] = preservation(current_files, baseline_files, current, baseline, reference)
    report["errors"].extend(preservation_errors)
    report["errors"].extend(resource_checks(current_files, current))
    report["errors"].extend(introduced_icons(current, baseline, icon_evidence))
    geometry_issues, report["geometry"] = geometry(current)
    old_geometry, report["baseline_geometry"] = geometry(baseline)
    current_quality = prose_issues(current) + duplicate_conditions(current) + geometry_issues
    baseline_quality = prose_issues(baseline) + duplicate_conditions(baseline) + old_geometry
    errors, warnings = classify_quality(current_quality, baseline_quality, reference)
    report["errors"].extend(errors)
    report["warnings"].extend(warnings)
    errors, unknown, report["registry"] = registry_checks(current, registry)
    report["errors"].extend(errors)
    report["unknown"].extend(unknown)
    errors, unknown, report["semantic_review"] = semantic_coverage(reviews or {}, baseline, baseline_commit)
    report["errors"].extend(errors)
    report["unknown"].extend(unknown)
    report["unknown"].extend([
        problem("gameplay_unverified", "Minecraft Forge 1.20.1", "Team credit, reward delivery, saved progress and trigger behavior require the exact client/server and a test world"),
        problem("rendering_unverified", reference, "Disk and straight-line geometry is an approximation, not a screenshot; actual FTB Quests rendering, labels and clipping require in-game inspection"),
        problem("semantics_unverified", "automation", "Parsing and resource resolution do not prove that advancement conditions match the promised action, or that rewards respect recipes and progression"),
    ])
    return finish(report)


def finish(report):
    report["summary"] = {"errors": len(report["errors"]), "warnings": len(report["warnings"]), "unknown": len(report["unknown"]),
                         "result": "fail" if report["errors"] else "pass_with_warnings_or_unknowns" if report["warnings"] or report["unknown"] else "pass"}
    report["issue_counts"] = {level: dict(sorted(Counter(i["code"] for i in report[level]).items())) for level in ("errors", "warnings", "unknown")}
    return report


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def snapshots(root, baseline):
    commit = git(root, "rev-parse", "--verify", baseline + "^{commit}").decode().strip()
    names = git(root, "ls-tree", "-r", "--name-only", "-z", commit, "--", *INPUT_ROOTS).decode().split("\0")
    baseline_files = {name: git(root, "show", f"{commit}:{name}") for name in names if name}
    current_files = {}
    for prefix in INPUT_ROOTS:
        directory = root / prefix
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                current_files[path.relative_to(root).as_posix()] = path.read_bytes()
    return current_files, baseline_files, commit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument("--reference", default=REFERENCE, help="Chapter filename without .snbt")
    parser.add_argument("--report", type=Path, default=Path("reports/quality.json"))
    parser.add_argument("--registry", type=Path, help="Optional registry evidence JSON; see docs/QUALITY_CHECKS.md")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.reference):
        parser.error("--reference must be a chapter filename without path or extension")
    try:
        root = args.root.resolve()
        current, baseline, commit = snapshots(root, args.baseline)
        registry = parse_json(args.registry.read_text(encoding="utf-8")) if args.registry else None
        reviews = {p.relative_to(root).as_posix(): parse_json(p.read_text(encoding="utf-8")) for p in sorted((root / "reviews").glob("semantic_*.json"))}
        icon_path = root / 'reviews/reference_icon_evidence.json'
        icon_evidence = parse_json(icon_path.read_text()) if icon_path.exists() else None
        report = evaluate(current, baseline, args.reference, registry, reviews, commit, icon_evidence)
        report_path = args.report if args.report.is_absolute() else root / args.report
        # Never let a report path overwrite protected game input files.
        relative = report_path.resolve().relative_to(root) if report_path.resolve().is_relative_to(root) else None
        if relative is not None and any(relative.as_posix() == prefix or relative.as_posix().startswith(prefix + "/") for prefix in INPUT_ROOTS):
            raise ValueError("Report path is inside protected quest/game data")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"report": str(report_path), "counts": report.get("counts"), **report["summary"]}, ensure_ascii=False))
        return 1 if report["errors"] else 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"quality: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
