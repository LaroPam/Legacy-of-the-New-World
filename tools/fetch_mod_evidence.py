#!/usr/bin/env python3
"""Download the author's public mod artifacts, verify hashes, index static evidence.

No Minecraft code is executed. Asset paths are evidence, not registry validation.
Signed Yandex URLs are kept only in memory. TLS verification stays enabled.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import shutil
import urllib.parse
import urllib.request
import zipfile

PUBLIC_FOLDER = "https://disk.yandex.ru/d/Q259pkIYuq7vEw"
PRIORITY = ("ftb-quests", "ftb-library", "mowziesmobs", "createbigcannons")
OMIT = ("AmbientSounds_", "zmedievalmusic-")


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/workspace/.onboarding/artifacts"))
    parser.add_argument("--output", type=Path, default=Path("reviews/artifact_evidence.json"))
    parser.add_argument("--priority-only", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    catalog = json.loads((repo / "references/mod_catalog.json").read_text())
    by_sha = {entry["sha256"]: entry for entry in catalog["mods"]}
    url = "https://cloud-api.yandex.net/v1/disk/public/resources?" + urllib.parse.urlencode(
        {"public_key": PUBLIC_FOLDER, "limit": 100}
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        listing = json.load(response)
    items = listing["_embedded"]["items"]
    if listing["_embedded"]["total"] != len(items):
        raise RuntimeError("Public listing is paginated; refusing an incomplete inventory")
    for item in items:
        if item.get("type") != "file" or not item["name"].endswith(".jar"):
            raise ValueError(f"Unexpected public folder entry: {item['name']}")
        if item["sha256"] not in by_sha:
            raise ValueError(f"Artifact absent from the pinned catalog: {item['name']}")
        if item["size"] != by_sha[item["sha256"]]["bytes"]:
            raise ValueError(f"Catalog size mismatch: {item['name']}")
    args.cache.mkdir(parents=True, exist_ok=True)
    selected = [i for i in items if not i["name"].startswith(OMIT)]
    if args.priority_only:
        selected = [i for i in selected if i["name"].startswith(PRIORITY)]
    selected.sort(key=lambda i: (not i["name"].startswith(PRIORITY), i["size"]))
    required = sum(i["size"] for i in selected)
    if required * 2 > shutil.disk_usage(args.cache).free:
        raise RuntimeError("Not enough disk space")

    def obtain(item: dict) -> dict:
        name = item["name"]
        if Path(name).name != name:
            raise ValueError("Unsafe artifact filename")
        target = args.cache / name
        if not target.exists() or digest(target) != item["sha256"]:
            temporary = target.with_suffix(".jar.partial")
            with urllib.request.urlopen(item["file"], timeout=120) as response:
                with temporary.open("wb") as handle:
                    shutil.copyfileobj(response, handle, length=1024 * 1024)
            if temporary.stat().st_size != item["size"] or digest(temporary) != item["sha256"]:
                temporary.unlink()
                raise ValueError(f"Artifact checksum failed: {name}")
            temporary.replace(target)
        with zipfile.ZipFile(target) as archive:
            if bad := archive.testzip():
                raise ValueError(f"Corrupt ZIP entry: {name}:{bad}")
            names = archive.namelist()
            models = sorted(
                f"{m[1]}:{m[2]}" for path in names
                if (m := re.fullmatch(r"assets/([^/]+)/models/item/(.+)\.json", path))
            )
            advancements = sorted(
                f"{m[1]}:{m[2]}" for path in names
                if (m := re.fullmatch(r"data/([^/]+)/advancements/(.+)\.json", path))
            )
            structures = sorted(
                f"{m[1]}:{m[2]}" for path in names
                if (m := re.fullmatch(r"data/([^/]+)/worldgen/structure/(.+)\.json", path))
            )
            biomes = sorted(
                f"{m[1]}:{m[2]}" for path in names
                if (m := re.fullmatch(r"data/([^/]+)/worldgen/biome/(.+)\.json", path))
            )
        print(f"verified {name} ({item['size']} bytes)", flush=True)
        return {
            "file": name, "catalog_file": by_sha[item["sha256"]]["file"],
            "sha256": item["sha256"], "bytes": item["size"],
            "status": "sha256_and_zip_crc_verified", "item_model_assets": models,
            "advancement_json": advancements, "structure_json": structures, "biome_json": biomes,
        }

    verified = []
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(obtain, item): item for item in selected}
        for future in concurrent.futures.as_completed(futures):
            try:
                verified.append(future.result())
            except Exception as error:
                item = futures[future]
                failures.append({"file": item["name"], "error": type(error).__name__ + ": " + str(error)})
                print(f"FAILED {item['name']}: {type(error).__name__}", flush=True)
    report = {
        "schema_version": 1, "public_folder": PUBLIC_FOLDER,
        "catalog_sha256": digest(repo / "references/mod_catalog.json"),
        "public_files": len(items), "public_bytes": sum(i["size"] for i in items),
        "all_public_sha256_match_catalog": True,
        "evidence_scope": "Static inspection only. Item model assets do not prove item registry IDs or valid rendering. Advancement JSON can be overridden or conditionally loaded. Minecraft client/server were not started.",
        "artifacts": sorted(verified, key=lambda x: x["file"].lower()),
        "not_downloaded": [{"file": i["name"], "sha256": i["sha256"], "bytes": i["size"],
                            "reason": "audio-only artifact not needed for quest static inspection" if i["name"].startswith(OMIT) else "priority-only run"}
                           for i in items if i not in selected],
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Evidence: {args.output}; verified={len(verified)}; failed={len(failures)}", flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
