# test_vectors.py

from srcvul.slices import parse_slice_profile_file
from srcvul.vectors import compute_vsvectors_for_file


def main():
    profiles = parse_slice_profile_file("demo_data/example_slices.txt")
    print(f"Parsed {len(profiles)} slice profiles.")

    # For this toy example, let's assume the module has 100 lines.
    module_size = 100

    vsvectors = compute_vsvectors_for_file(profiles, module_size)
    for v in vsvectors:
        print("----")
        print(f"file: {v.file_path}")
        print(f"function: {v.function}")
        print(f"variable: {v.variable}")
        print(f"SC:   {v.sc:.4f}")
        print(f"SCvg: {v.scvg:.4f}")
        print(f"SI:   {v.si:.4f}")
        print(f"SS:   {v.ss:.4f}")
        print(f"as_array: {v.as_array()}")


if __name__ == "__main__":
    main()

