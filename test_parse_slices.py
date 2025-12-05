# test_parse_slices.py

from srcvul.slices import parse_slice_profile_file

def main():
    profiles = parse_slice_profile_file("demo_data/example_slices.txt")
    print(f"Parsed {len(profiles)} slice profiles.")
    for p in profiles:
        print("----")
        print(f"file: {p.file_path}")
        print(f"function: {p.function}")
        print(f"variable: {p.variable}")
        print(f"def_lines: {p.def_lines}")
        print(f"use_lines: {p.use_lines}")
        print(f"dvars: {p.dvars}")
        print(f"ptrs: {p.ptrs}")
        print(f"cfuncs: {p.cfuncs}")
        print(f"slice_lines: {p.slice_lines}")

if __name__ == "__main__":
    main()

