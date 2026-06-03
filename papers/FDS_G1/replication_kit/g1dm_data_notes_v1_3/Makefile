.PHONY: plan dirs demo note2 note3 note4 test

plan:
	PYTHONPATH=src python scripts/download_data.py --print-plan

dirs:
	PYTHONPATH=src python scripts/download_data.py --make-dirs

demo:
	PYTHONPATH=src python notes/note1_carrier_floor.py --allow-demo --out outputs/note1_demo
	PYTHONPATH=src python notes/note2_mu_growth_leakage.py --out outputs/note2_demo
	PYTHONPATH=src python notes/note3_lensing_growth_split.py --out outputs/note3_demo
	PYTHONPATH=src python notes/note4_sro_sparse_audit.py --out outputs/note4_demo

note2:
	PYTHONPATH=src python notes/note2_mu_growth_leakage.py --out outputs/note2

note3:
	PYTHONPATH=src python notes/note3_lensing_growth_split.py --out outputs/note3

note4:
	PYTHONPATH=src python notes/note4_sro_sparse_audit.py --out outputs/note4

test:
	PYTHONPATH=src python -m pytest tests/ -v --tb=short
