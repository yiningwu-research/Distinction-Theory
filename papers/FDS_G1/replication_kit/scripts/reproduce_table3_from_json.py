#!/usr/bin/env python3
"""Reproduce v1.2 Table 3 from per-seed JSON files.

Usage:
    python reproduce_table3_from_json.py \
        --input-dir ../production_evidence_v1_2/outputs_medium_8seed/per_seed_json \
        --output-dir . \
        --reference-model g1dem34
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__),
    '../production_evidence_v1_2/src'))
from generate_evidence_tables import main

if __name__ == '__main__':
    main()
