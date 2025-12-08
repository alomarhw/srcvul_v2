# srcVul v2 – Slicing-Based Vulnerable Code Clone Detection (Prototype)

srcVul v2 is a lightweight, re-implemented prototype of the original srcVul vulnerability detection tool.  
It demonstrates how program slicing vectors can be used to identify vulnerable code clones and recommend patches.

This prototype is intended for reproducible research. It implements core ideas from:

H. Alomari et al., 2025  
"A Slicing-Based Approach for Detecting and Patching Vulnerable Code Clones."

This is not the full research artifact. It is a simplified and clean version focused on clarity and reproducibility.

---

## Repository Structure

```
srcvul/
  __init__.py
  cli.py
  slices.py
  vectors.py
  similarity.py
  db.py

demo_data/
  vuln_parent_slices.txt
  target_parent_slices.txt
  libvirt-1.1.0.slice.xml
  libvirt_slices.txt

requirements.txt
LICENSE
README.md
```

---

## Installation

Python 3.10 or later is required.

### macOS / Linux

```
git clone https://github.com/alomarhw/srcvul_v2.git
cd srcvul_v2

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Windows (PowerShell)

```
git clone https://github.com/alomarhw/srcvul_v2.git
cd srcvul_v2

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## One-Command Demo (Motivating Example)

To run the motivating example for CVE-2019-15214:

```
python -m srcvul.cli demo-motivating
```

This command:

1. Builds a vulnerability database from `demo_data/vuln_parent_slices.txt`
2. Scans `demo_data/target_parent_slices.txt`
3. Reports detected vulnerable clones and prints the associated patch text

Example output:

```
[build-db] Saved N entries to demo_data/vuln_db_cve_2019_15214_demo.json
[scan] Found 1 matches with threshold 0.80
----
target: Linux-4.14.76/.../snd_info_create_entry:parent
db:     vuln_id=CVE-2019-15214
sim:    1.0000
patch:  Fix: hold the parent instance until all operations complete...
```

---

## Manual Usage

### 1. Build a vulnerability database

```
python -m srcvul.cli build-db \
  --slices demo_data/vuln_parent_slices.txt \
  --module-size 24 \
  --vuln-id CVE-2019-15214 \
  --patch-text "Fix: hold the parent instance until all operations complete; prevent stale pointer dereference." \
  --out demo_data/vuln_db_cve_2019_15214.json
```

### 2. Scan a target file

```
python -m srcvul.cli scan \
  --slices demo_data/target_parent_slices.txt \
  --module-size 22 \
  --db demo_data/vuln_db_cve_2019_15214.json \
  --threshold 0.8
```

### 3. Scan a larger dataset (libvirt example)

```
python -m srcvul.cli scan \
  --slices demo_data/libvirt_slices.txt \
  --module-size 10000 \
  --db demo_data/vuln_db_cve_2019_15214.json \
  --threshold 0.8
```

---

## How the Tool Works

1. Slice profiles are parsed to extract:
   - variable name
   - def and use lines
   - dependent variables
   - pointer relationships
   - called functions

2. Slicing vectors (SC, SCvg, SI, SS) are computed for each slice.

3. Cosine similarity is used to compare vectors and identify clone-like patterns.

4. Patch recommendations are displayed when a match is found.

---

## License

This project is released under the MIT License.  
See the LICENSE file for details.

---

## Citation

If you use this tool in academic work, please cite:

H. Alomari et al., 2025  
"A Slicing-Based Approach for Detecting and Patching Vulnerable Code Clones."
