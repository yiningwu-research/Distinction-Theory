#!/bin/bash
# Run all D7 tests: reference implementation + standalone package
set -e
echo "=== D7 reference implementation ==="
python3 reference_impl/d7_markov_toy.py
echo ""
echo "=== D7 standalone package ==="
cd d7_markov_screen && python3 d7_markov_screen_toy.py && python3 test_d7_markov_screen_toy.py && cd ..
echo ""
echo "=== All model identity checks ==="
python3 reference_impl/models.py
echo ""
echo "=== All validation tests ==="
python3 -c "
import sys
sys.path.insert(0, 'validation_tests')
sys.path.insert(0, 'reference_impl')
import test_model_identities, test_d7_markov_toy, test_prior_bounds, test_expected_chi2
ok = True
for mod in [test_model_identities, test_d7_markov_toy, test_prior_bounds, test_expected_chi2]:
    for name in sorted(dir(mod)):
        if name.startswith('test_'):
            try:
                getattr(mod, name)()
            except Exception as e:
                ok = False
                print(f'FAIL: {mod.__name__}.{name}: {e}')
print(f'ALL PASS: {ok}')
"
