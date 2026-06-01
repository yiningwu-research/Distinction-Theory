"""Generate v1.2 production-refined evidence tables from per-seed JSONs.

Usage:
    python generate_evidence_tables.py \
        --input-dir ../outputs_medium_8seed/per_seed_json \
        --output-dir ../outputs_medium_8seed \
        --reference-model g1dem34

Outputs (in --output-dir):
    production_8seed_summary.csv      Per-model aggregated statistics
    production_8seed_table3.csv       Table 3 styled output
    production_8seed_manifest.json    Full provenance manifest
"""

import argparse, csv, json, os, re, statistics, glob, sys


def load_all_jsons(input_dir):
    records = []
    for f in sorted(glob.glob(os.path.join(input_dir, "*_nested_evidence.json"))):
        with open(f) as fh:
            d = json.load(fh)
        records.append(d)
    return records


def model_sort_key(m):
    order = ["g1dem34", "g1demk", "g1deconstsig", "g1de2", "g1de1", "cpl", "lcdm"]
    try:
        return order.index(m)
    except ValueError:
        return 999


def aggregate(records):
    models = {}
    for r in records:
        m = r["model"]
        if m not in models:
            models[m] = []
        models[m].append(r)
    return models


def compute_stats(records, reference_model, ref_mean):
    n = len(records)
    logZs = [r["logZ"] for r in records]
    logZ_errs = [r["logZ_err"] for r in records]
    ncalls = [r["ncall"] for r in records]

    mean_z = statistics.mean(logZs)
    if n >= 2:
        m = statistics.mean(logZs)
        scatter = (sum((x - m)**2 for x in logZs) / (n - 1))**0.5
    else:
        scatter = 0.0
    mean_err = (sum(e**2 for e in logZ_errs) / n) ** 0.5

    seeds = sorted([r["seed"] for r in records])
    nlives = list(set(r["nlive"] for r in records))
    nlive_str = str(nlives[0]) if len(nlives) == 1 else f"{min(nlives)}-{max(nlives)}"

    delta = mean_z - ref_mean if ref_mean is not None else None
    bf = None
    if delta is not None:
        bf_num = None
        try:
            bf_num = float(delta)
        except TypeError:
            pass
        bf = f"{bf_num:.2e}" if bf_num is not None else None

    all_within_2sigma = True
    for r in records:
        if abs(r["logZ"] - mean_z) > 2 * r["logZ_err"]:
            all_within_2sigma = False
            break

    return {
        "model": records[0]["model"],
        "n": n,
        "seeds": seeds,
        "nlive": nlive_str,
        "mean_logZ": mean_z,
        "scatter": scatter,
        "mean_logZ_err": mean_err,
        "total_ncall": sum(ncalls),
        "delta_logZ": delta,
        "bayes_factor": bf,
        "all_within_2sigma": all_within_2sigma,
        "logZ_min": min(logZs),
        "logZ_max": max(logZs),
    }


def write_summary_csv(stats_list, path):
    fieldnames = [
        "model", "n", "seeds", "nlive", "mean_logZ", "scatter",
        "mean_logZ_err", "total_ncall", "delta_logZ_ref",
        "bayes_factor_ref", "all_within_2sigma",
    ]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for s in stats_list:
            row = {
                "model": s["model"],
                "n": s["n"],
                "seeds": ";".join(str(x) for x in s["seeds"]),
                "nlive": s["nlive"],
                "mean_logZ": f"{s['mean_logZ']:.6f}",
                "scatter": f"{s['scatter']:.6f}",
                "mean_logZ_err": f"{s['mean_logZ_err']:.6f}",
                "total_ncall": s["total_ncall"],
                "delta_logZ_ref": f"{s['delta_logZ']:.6f}" if s["delta_logZ"] is not None else "",
                "bayes_factor_ref": s["bayes_factor"] if s["bayes_factor"] else "",
                "all_within_2sigma": s["all_within_2sigma"],
            }
            w.writerow(row)


def write_table3_csv(stats_list, path):
    fieldnames = [
        "model", "n_seeds", "logZ_mean", "logZ_scatter",
        "logZ_mean_err", "delta_logZ_vs_ref", "bayes_factor_vs_ref",
    ]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for s in stats_list:
            row = {
                "model": s["model"],
                "n_seeds": s["n"],
                "logZ_mean": f"{s['mean_logZ']:.3f}",
                "logZ_scatter": f"{s['scatter']:.3f}",
                "logZ_mean_err": f"{s['mean_logZ_err']:.3f}",
                "delta_logZ_vs_ref": f"{s['delta_logZ']:.3f}" if s["delta_logZ"] is not None else "0.000",
                "bayes_factor_vs_ref": s["bayes_factor"] if s["bayes_factor"] else "1",
            }
            w.writerow(row)


def write_manifest(records, stats_list, path):
    models_meta = {}
    for s in stats_list:
        models_meta[s["model"]] = s

    manifest = {
        "kit_version": "v1.2",
        "production_run": "medium_8seed_dlogz0.1",
        "dynesty_version": "3.0.0",
        "date_completed": "2026-06-01",
        "total_seeds": sum(s["n"] for s in stats_list),
        "total_jobs": sum(s["n"] for s in stats_list),
        "models": {},
        "claim_boundary": (
            "stage-2d exact likelihood production-refined audit; "
            "not full 3x2pt; not final cosmological confirmation"
        ),
    }
    for s in stats_list:
        m = s["model"]
        manifest["models"][m] = {
            "n_seeds": s["n"],
            "seeds": s["seeds"],
            "nlive": s["nlive"],
            "mean_logZ": round(s["mean_logZ"], 6),
            "scatter": round(s["scatter"], 6),
            "mean_logZ_err": round(s["mean_logZ_err"], 6),
            "total_ncall": s["total_ncall"],
            "delta_logZ_vs_ref": round(s["delta_logZ"], 6) if s["delta_logZ"] is not None else 0.0,
            "all_within_2sigma": s["all_within_2sigma"],
        }

    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate v1.2 production evidence tables")
    parser.add_argument("--input-dir", default="outputs_medium_8seed/per_seed_json")
    parser.add_argument("--output-dir", default="outputs_medium_8seed")
    parser.add_argument("--reference-model", default="g1dem34")
    args = parser.parse_args()

    records = load_all_jsons(args.input_dir)
    if not records:
        print("Error: no JSON files found in", args.input_dir)
        sys.exit(1)

    by_model = aggregate(records)

    # Determine reference model mean
    ref_records = by_model.get(args.reference_model)
    if not ref_records:
        print(f"Error: reference model '{args.reference_model}' not found in data")
        sys.exit(1)
    ref_mean = statistics.mean(r["logZ"] for r in ref_records)
    print(f"Reference model: {args.reference_model}  mean logZ = {ref_mean:.6f}")

    # Compute stats for all models
    stats_list = []
    for m in sorted(by_model.keys(), key=model_sort_key):
        s = compute_stats(by_model[m], args.reference_model, ref_mean)
        stats_list.append(s)
        in_2s = "yes" if s["all_within_2sigma"] else "NO"
        print(f"  {m:14s} n={s['n']}  mean={s['mean_logZ']:.3f}  "
              f"scatter={s['scatter']:.4f}  Δ={s['delta_logZ']:.3f}  "
              f"2σ={in_2s}")

    os.makedirs(args.output_dir, exist_ok=True)

    sum_path = os.path.join(args.output_dir, "production_8seed_summary.csv")
    write_summary_csv(stats_list, sum_path)
    print(f"\nWrote {sum_path}")

    t3_path = os.path.join(args.output_dir, "production_8seed_table3.csv")
    write_table3_csv(stats_list, t3_path)
    print(f"Wrote {t3_path}")

    man_path = os.path.join(args.output_dir, "production_8seed_manifest.json")
    write_manifest(records, stats_list, man_path)
    print(f"Wrote {man_path}")

    # Check for scatter > 0.15
    for s in stats_list:
        if s["scatter"] > 0.15:
            print(f"NOTE: {s['model']} scatter {s['scatter']:.4f} exceeds 0.15 "
                  f"(ranking unaffected, see CLAIM_STATUS.md)")


if __name__ == "__main__":
    main()
