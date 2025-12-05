import argparse
import xml.etree.ElementTree as ET
from typing import List


def parse_int_list(s: str) -> List[int]:
    """
    Parse a comma-separated list of integers like '697' or '714,716,717'.
    """
    if not s:
        return []
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def parse_str_list(s: str) -> List[str]:
    """
    Parse a comma-separated list of identifiers like 'parent,child'.
    """
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Convert libvirt-1.1.0.slice.xml to srcvul text slice profiles"
    )
    parser.add_argument("--xml", required=True, help="Path to libvirt-1.1.0.slice.xml")
    parser.add_argument("--out", required=True, help="Output text file")
    args = parser.parse_args()

    tree = ET.parse(args.xml)
    root = tree.getroot()

    lines_out: List[str] = []

    # ⚠️ IMPORTANT:
    # I have to guess the XML schema here. You will likely need to:
    # - print out the first few elements from your XML to confirm tag/attribute names
    # - adjust the code below accordingly.
    #
    # Common srcSlice-style structures:
    #   <slices>
    #     <slice file="..." function="..." variable="...">
    #       <def>697</def>
    #       <use>714,716,717</use>
    #       <dvars>...</dvars>
    #       <ptrs>...</ptrs>
    #       <cfuncs>list_add_tail{2}</cfuncs>
    #     </slice>
    #   </slices>
    #
    # If your XML differs, tweak the tag/attribute names below.

    for slice_el in root.findall(".//slice"):
        # Try attributes first
        file_path = (
            slice_el.get("file")
            or slice_el.findtext("file")
            or ""
        )
        function = (
            slice_el.get("function")
            or slice_el.findtext("function")
            or ""
        )
        variable = (
            slice_el.get("variable")
            or slice_el.findtext("variable")
            or ""
        )

        # Children for def/use/dvars/ptrs/cfuncs
        def_text = slice_el.findtext("def") or slice_el.findtext("defs") or ""
        use_text = slice_el.findtext("use") or slice_el.findtext("uses") or ""
        dvars_text = slice_el.findtext("dvars") or ""
        ptrs_text = slice_el.findtext("ptrs") or slice_el.findtext("pointers") or ""
        cfuncs_text = slice_el.findtext("cfuncs") or ""

        # Normalize into our format
        def_lines = parse_int_list(def_text)
        use_lines = parse_int_list(use_text)
        dvars = parse_str_list(dvars_text)
        ptrs = parse_str_list(ptrs_text)

        # cfuncs: if your XML encodes them differently, you may need to adjust this.
        # For a simple assumption, we just keep whatever string is there,
        # e.g., "list_add_tail{2},kfree{1}"
        cfuncs = cfuncs_text.strip()

        # Build textual line in the format our srcvul.slices parser expects
        line = (
            f"{file_path},{function},{variable},"
            f"def{{{','.join(str(x) for x in def_lines)}}},"
            f"use{{{','.join(str(x) for x in use_lines)}}},"
            f"dvars{{{','.join(dvars)}}},"
            f"ptrs{{{','.join(ptrs)}}},"
            f"cfuncs{{{cfuncs}}}"
        )
        lines_out.append(line)

    with open(args.out, "w", encoding="utf-8") as f:
        for line in lines_out:
            f.write(line + "\n")

    print(f"Wrote {len(lines_out)} slice profiles to {args.out}")


if __name__ == "__main__":
    main()

