#!/usr/bin/env python3
"""Generate the raw English wiki html from the reference portal's English specs.

The monorepo generator (scripts/generate/generate_api_wiki.py) reads its zh specs
from `docker/specs` and hardcodes its output paths. The English wiki needs pages
whose *content* strings are English too, and the zh swagger specs carry Chinese
content strings — so for `en` we re-run the SAME generator against the English
specs that live in the reference portal:

    <sites>/reference/public/specs/<service>-en.json   (swagger 2.0)

The generator's path constants are patched in-memory (no edits to the monorepo).
Services without an `-en.json` spec are skipped by the generator with a [WARN]
(their service pages render the portal's "not indexed" fallback).

Output layout (temp dir, regenerated from scratch on every run):
    <out>/specs/<service>/swagger.json   staged spec inputs
    <out>/md/                            generator's .md output (unused, kept out)
    <out>/html/                          raw html — feed this to sync-wiki.py

Usage:
    python scripts/gen-wiki-en.py [--out <dir>] [--specs-src <dir>] [--generator <file>]
    python scripts/sync-wiki.py --lang en --src <out>/html
"""

import argparse
import importlib.util
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_GENERATOR = r"D:\go\auth_ms_new\scripts\generate\generate_api_wiki.py"
DEFAULT_SPECS_SRC = os.path.join(os.path.dirname(REPO_ROOT), "reference", "public", "specs")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate raw English wiki html from reference en specs")
    parser.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "autional-wiki-en-gen"),
                        help="temp working dir (default: %(default)s)")
    parser.add_argument("--specs-src", default=DEFAULT_SPECS_SRC,
                        help="dir holding <service>-en.json (default: %(default)s)")
    parser.add_argument("--generator", default=DEFAULT_GENERATOR,
                        help="monorepo generator script (default: %(default)s)")
    args = parser.parse_args()

    if not os.path.isfile(args.generator):
        print(f"ERROR: generator not found: {args.generator}")
        return 1
    if not os.path.isdir(args.specs_src):
        print(f"ERROR: specs dir not found: {args.specs_src}")
        return 1

    out = os.path.abspath(args.out)
    specs_dir = os.path.join(out, "specs")
    md_dir = os.path.join(out, "md")
    html_dir = os.path.join(out, "html")
    for d in (specs_dir, md_dir, html_dir):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    staged = 0
    for name in sorted(os.listdir(args.specs_src)):
        if not name.endswith("-en.json"):
            continue
        svc = name[: -len("-en.json")]
        svc_dir = os.path.join(specs_dir, svc)
        os.makedirs(svc_dir, exist_ok=True)
        shutil.copyfile(os.path.join(args.specs_src, name), os.path.join(svc_dir, "swagger.json"))
        staged += 1
    print(f"staged {staged} en specs -> {specs_dir}")
    if staged == 0:
        print("ERROR: no <service>-en.json specs found")
        return 1

    spec = importlib.util.spec_from_file_location("generate_api_wiki", args.generator)
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    gen.SPECS_DIR = specs_dir
    gen.OUTPUT_DIR = md_dir
    gen.ENDPOINTS_DIR = os.path.join(md_dir, "endpoints")
    gen.HTML_OUTPUT_DIR_DEFAULT = html_dir
    sys.argv = [args.generator, "--html"]

    try:
        rc = gen.main()
    except SystemExit as exc:  # generator may sys.exit() instead of returning
        rc = exc.code or 0
    if rc:
        print(f"ERROR: generator failed (rc={rc})")
        return int(rc)

    if not os.path.isdir(os.path.join(html_dir, "api")):
        print(f"ERROR: generator produced no api/ output under {html_dir}")
        return 1
    print(f"raw html dir: {html_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
