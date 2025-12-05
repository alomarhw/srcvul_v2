# srcvul/cli.py

import argparse
from typing import List

from .slices import parse_slice_profile_file
from .vectors import compute_vsvectors_for_file
from .db import VulDBEntry, save_db, load_db
from .similarity import find_matches


def cmd_build_db(args: argparse.Namespace) -> None:
    """
    Build a tiny vulnerability DB from a slice-profile file.
    For simplicity, every slice profile in this file becomes an entry
    with the same vuln_id (e.g., a CVE ID or label).
    """
    profiles = parse_slice_profile_file(args.slices)
    vsvectors = compute_vsvectors_for_file(profiles, args.module_size)

    entries: List[VulDBEntry] = [
        VulDBEntry.from_vsvect(v, vuln_id=args.vuln_id, patch=args.patch_text)
        for v in vsvectors
    ]

    save_db(args.out, entries)
    print(f"[build-db] Saved {len(entries)} entries to {args.out}")


def cmd_scan(args: argparse.Namespace) -> None:
    """
    Scan target slice profiles against a vulnerability DB.
    """
    # Load target slices and compute vectors
    profiles = parse_slice_profile_file(args.slices)
    target_vectors = compute_vsvectors_for_file(profiles, args.module_size)

    # Load DB entries and convert to VSVect
    db_entries = load_db(args.db)
    db_vectors = [e.to_vsvect() for e in db_entries]

    matches = find_matches(target_vectors, db_vectors, threshold=args.threshold)

    print(f"[scan] Found {len(matches)} matches with threshold {args.threshold:.2f}")

    for m in matches:
        print("----")
        print(f"target: {m.target.file_path}:{m.target.function}:{m.target.variable}")

        # Find the matching DB entry (by metadata + vector fields)
        matched_entry = None
        for e in db_entries:
            if (
                e.file_path == m.db.file_path
                and e.function == m.db.function
                and e.variable == m.db.variable
                and abs(e.sc - m.db.sc) < 1e-9
                and abs(e.scvg - m.db.scvg) < 1e-9
                and abs(e.si - m.db.si) < 1e-9
                and abs(e.ss - m.db.ss) < 1e-9
            ):
                matched_entry = e
                break

        if matched_entry is not None:
            print(
                f"db:     vuln_id={matched_entry.vuln_id}, "
                f"{matched_entry.file_path}:{matched_entry.function}:{matched_entry.variable}"
            )
            print(f"sim:    {m.similarity:.4f}")
            if matched_entry.patch:
                print("patch:")
                print(matched_entry.patch)
        else:
            print("db:     (no matching DB entry found)")
            print(f"sim:    {m.similarity:.4f}")


def cmd_demo_motivating(args: argparse.Namespace) -> None:
    """
    Run the motivating example demo in one command:
      1. Build a small vuln DB for CVE-2019-15214 from demo_data/vuln_parent_slices.txt
      2. Scan demo_data/target_parent_slices.txt against that DB
    """
    from types import SimpleNamespace
    import os

    # Paths relative to project root (where you run the command)
    vuln_slices_path = "demo_data/vuln_parent_slices.txt"
    target_slices_path = "demo_data/target_parent_slices.txt"
    db_path = "demo_data/vuln_db_cve_2019_15214_demo.json"

    # Sanity check
    if not os.path.exists(vuln_slices_path):
        print(f"[demo-motivating] Missing vuln slices file: {vuln_slices_path}")
        return
    if not os.path.exists(target_slices_path):
        print(f"[demo-motivating] Missing target slices file: {target_slices_path}")
        return

    print("[demo-motivating] Step 1/2: building vulnerability DB for CVE-2019-15214...")
    build_args = SimpleNamespace(
        slices=vuln_slices_path,
        module_size=24,  # module size from the paper for snd_info_create_entry
        vuln_id="CVE-2019-15214",
        patch_text=(
            "Fix: hold the parent instance until all operations complete; "
            "prevent stale pointer dereference in snd_info_create_entry."
        ),
        out=db_path,
    )
    cmd_build_db(build_args)

    print("\n[demo-motivating] Step 2/2: scanning target parent slice...")
    scan_args = SimpleNamespace(
        slices=target_slices_path,
        module_size=22,  # target module size from the paper
        db=db_path,
        threshold=0.8,
    )
    cmd_scan(scan_args)

    print("\n[demo-motivating] Done.")




def main() -> None:
    parser = argparse.ArgumentParser(
        description="srcVul v2 (toy implementation) CLI"
    )
    subparsers = parser.add_subparsers(dest="command")

    # build-db
    p_build = subparsers.add_parser(
        "build-db",
        help="Build a tiny vulnerability DB from slice profiles",
    )
    p_build.add_argument(
        "--slices",
        required=True,
        help="Path to slice-profile text file",
    )
    p_build.add_argument(
        "--module-size",
        type=int,
        required=True,
        help="Total number of lines in the module/file (including whitespace)",
    )
    p_build.add_argument(
        "--vuln-id",
        required=True,
        help="Identifier for this vulnerability (e.g., CVE-XXXX-YYYY or a label)",
    )
    p_build.add_argument(
        "--patch-text",
        default="",
        help="Short description or snippet of the patch associated with this vulnerability",
    )
    p_build.add_argument(
        "--out",
        required=True,
        help="Output JSON file for the vulnerability DB",
    )
    p_build.set_defaults(func=cmd_build_db)

    # scan
    p_scan = subparsers.add_parser(
        "scan",
        help="Scan target slice profiles against an existing vulnerability DB",
    )
    p_scan.add_argument(
        "--slices",
        required=True,
        help="Path to target slice-profile text file",
    )
    p_scan.add_argument(
        "--module-size",
        type=int,
        required=True,
        help="Total number of lines in the target module/file",
    )
    p_scan.add_argument(
        "--db",
        required=True,
        help="Path to JSON vulnerability DB file created by build-db",
    )
    p_scan.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Cosine similarity threshold (default: 0.8)",
    )
    p_scan.set_defaults(func=cmd_scan)

    # demo-motivating (stub)
    p_demo = subparsers.add_parser(
        "demo-motivating",
        help="Run the motivating example demo (stub for now)",
    )
    p_demo.set_defaults(func=cmd_demo_motivating)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
