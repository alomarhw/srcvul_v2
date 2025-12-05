# srcVul v2 – Slicing-Based Vulnerable Code Clone Detection (Prototype)

This repository contains a lightweight, **re-implemented prototype** of the `srcVul` tool for detecting vulnerable code clones and recommending patches using **program slicing vectors**.

It is based on the methodology described in:

> *A Slicing-Based Approach for Detecting and Patching Vulnerable Code Clones*  
> H. Alomari et al., 2025.  

The goal of this repository is to provide a **clean, reproducible, ICPC-style tool demo** that showcases the core ideas:

- Build a **vulnerability database** from slice profiles of known vulnerable code (e.g., CVE-2019-15214).
- Compute **slicing vectors** (vsvectors) for target code slices.
- Use **cosine similarity** to detect vulnerable clones.
- Attach a **patch description** to each vulnerability and show it for detected clones.

This is **not** the original research artifact from the paper, but a simplified, scriptable version designed for teaching, replication, and tool demonstrations.

---

## Repository Structure

```text
srcvul/
  __init__.py        # package init
  slices.py          # SliceProfile model + text parser
  vectors.py         # vsvector (VSVect) computation
  similarity.py      # cosine similarity + brute-force match search
  db.py              # JSON-based vulnerability DB (VulDBEntry)
  cli.py             # command-line interface (build-db, scan, demo-motivating)

demo_data/
  vuln_parent_slices.txt         # vulnerability slice profiles (e.g., CVE-2019-15214)
  target_parent_slices.txt       # target slice profile for the motivating example
  libvirt-1.1.0.slice.xml        # original libvirt slices file (srcVul data format)
  libvirt_slices.txt             # same as above, but with `pointers` renamed to `ptrs`

requirements.txt                 # Python dependencies (minimal)
README.md

