#!/bin/bash
set -e
echo "=== KiDS shear-only environment check ==="

# Check Python
python3 -c "import numpy; print('numpy:', numpy.__version__)" 2>/dev/null || echo "MISSING: numpy"
python3 -c "import scipy; print('scipy:', scipy.__version__)" 2>/dev/null || echo "MISSING: scipy"
python3 -c "import pandas; print('pandas:', pandas.__version__)" 2>/dev/null || echo "MISSING: pandas"
python3 -c "import yaml; print('pyyaml:', yaml.__version__)" 2>/dev/null || echo "MISSING: pyyaml"

# Check CLASS (optional)
python3 -c "import classy; print('classy:', classy.__version__)" 2>/dev/null || echo "CLASS not installed (required for KiDS Pk backend)"

# Check plotting (optional)
python3 -c "import matplotlib; print('matplotlib:', matplotlib.__version__)" 2>/dev/null || echo "matplotlib not installed (needed for figures)"

# Check sampler (optional)
python3 -c "import dynesty; print('dynesty:', dynesty.__version__)" 2>/dev/null || echo "dynesty not installed (needed for nested sampling)"
python3 -c "import emcee; print('emcee:', emcee.__version__)" 2>/dev/null || echo "emcee not installed"

echo ""
echo "=== Done ==="
