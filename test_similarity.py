# test_similarity.py

from srcvul.slices import parse_slice_profile_file
from srcvul.vectors import compute_vsvectors_for_file
from srcvul.similarity import find_matches, cosine_similarity


def main():
    profiles = parse_slice_profile_file("demo_data/example_slices.txt")
    module_size = 100  # same as in test_vectors

    vsvectors = compute_vsvectors_for_file(profiles, module_size)

    print(f"Got {len(vsvectors)} vectors.")

    # For a simple test, treat:
    # - the first vector as the "DB" (known vulnerable slice)
    # - both vectors as the "target" set.
    db_vectors = [vsvectors[0]]
    target_vectors = vsvectors

    # Show cosine similarity between the two manually:
    print("\nPairwise cosine similarities:")
    for i, t in enumerate(target_vectors):
        for j, db in enumerate(db_vectors):
            sim = cosine_similarity(t.as_array(), db.as_array())
            print(f"target {i} vs db {j}: {sim:.4f}")

    # Now use find_matches with a low threshold to see matches.
    matches = find_matches(target_vectors, db_vectors, threshold=0.0)
    print(f"\nfind_matches returned {len(matches)} matches.")
    for m in matches:
        print("----")
        print(f"target: {m.target.variable}, db: {m.db.variable}, sim: {m.similarity:.4f}")


if __name__ == "__main__":
    main()

