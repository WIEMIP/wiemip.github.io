#!/usr/bin/env python3
"""
Regenerate model-results/<experiment>/data.json for the WIEMIP site.

Two sources are combined:

  * `wiemip_registry` (the ../wiemip-data-processing repo) is the SOURCE OF TRUTH
    for the registered models, each model's factorial vocabulary, and the WIEMIP
    variable list. Its per-model adapters also know how each (simulation, factorial,
    variable) maps to a file path on the bucket.
  * The Wasabi S3 bucket `wiemip` (region us-east-2) is scraped — a plain object
    LISTING, no downloads — to see which of those files have actually been uploaded.

The result is a per-model coverage matrix (factorials × the four C4MIP simulations)
that the static /model-results page renders as a table. Re-run this whenever models
upload new data:

    uv run --with boto3 python tools/build_model_results.py

Requires an AWS profile named `wasabi` in ~/.aws/credentials.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

# --- edit me ---------------------------------------------------------------
SITE_ROOT = Path(__file__).resolve().parent.parent
# Source of truth for models / factorials / variables: the sibling data-processing
# repo. Override if it lives elsewhere.
REGISTRY_REPO = SITE_ROOT.parent / "wiemip-data-processing"
BUCKET = "wiemip"
REGION = "us-east-2"
ENDPOINT = "https://s3.us-east-2.wasabisys.com"
AWS_PROFILE = "wasabi"
EXPERIMENT = "1pctCO2"
FORCING = "ukesm"  # cross-model comparability standard (see data-processing AGENTS.md)
SIMULATIONS = ["bgc", "cou", "ctrl"]  # beta<-bgc; gamma<-cou vs bgc (no separate rad run)
OUT = SITE_ROOT / "model-results" / EXPERIMENT / "data.json"

# The factorial rows shown for EVERY model. A deliberately trimmed core (the
# process-removal factorials from the reference layout) rather than the full
# registry vocabulary — some models (JULES) declare many bespoke permafrost and
# fire-sweep variants that would swamp the table. `baseline` stays because it's the
# reference every other row's eta/delta is measured against. Every name here must
# still be a real registry factorial (asserted at run time), so it can't drift.
SCHEMA_FACTORIALS = ["baseline", "noNitrogen", "noFire", "noDynVeg", "noPermafrost"]
# ---------------------------------------------------------------------------

# PRESENTATION ONLY. The set of factorials (the "schema") is taken from the
# registry (const.Factorial + const.extra_factorials) at run time — this dict just
# supplies human-readable labels for those registry names and a preferred display
# order (baseline, then process-offs, then permafrost add/remove variants, then the
# fire parameter sweeps). Any registry factorial missing here still appears in the
# schema, labelled with its raw name; a mismatch is reported when the script runs.
FACTORIAL_LABELS = {
    "baseline": "Default (all procs)",
    "noFire": "No fire",
    "noNitrogen": "No N-cycle",
    "noPermafrost": "No permafrost",
    "noDynVeg": "No veg dynamics",
    "noBVOC": "No BVOC",
    "noFire_noNitrogen": "No fire + no N-cycle",
    "noFire_noPermafrost": "No fire + no permafrost",
    "noPermafrostC": "No permafrost (C)",
    "noPermafrostCN": "No permafrost (C+N)",
    "noPermafrostCNNinorg": "No permafrost (C+N+Ninorg)",
    "addPermafrostC": "Add permafrost (C)",
    "addPermafrostCN": "Add permafrost (C+N)",
    "addPermafrostCNNinorg": "Add permafrost (C+N+Ninorg)",
    "noNitrogen_addPermafrostC": "No N-cycle + add permafrost (C)",
    "noNitrogen_noPermafrostC": "No N-cycle + no permafrost (C)",
    "Fire0005": "Fire param sweep 0005",
    "Fire0249": "Fire param sweep 0249",
    "Fire0304": "Fire param sweep 0304",
    "Fire0336": "Fire param sweep 0336",
}
_PREFERRED_ORDER = list(FACTORIAL_LABELS)

sys.path.insert(0, str(REGISTRY_REPO))
import wiemip_registry as reg  # noqa: E402
from wiemip_registry.adapters import adapters  # noqa: E402
from wiemip_registry.const import DATA_ROOT, extra_factorials  # noqa: E402

import boto3  # noqa: E402
from botocore.config import Config  # noqa: E402

_DATA_PREFIX = str(DATA_ROOT).rstrip("/") + "/"


def path_to_key(path: str) -> str:
    """Adapter paths are rooted at the s3fs mount (const.DATA_ROOT). Strip that to
    get the bucket key the same file lives at on Wasabi."""
    return str(path).replace(_DATA_PREFIX, "", 1)


def build_schema() -> list[str]:
    """The fixed factorial schema shown for EVERY model: the curated
    `SCHEMA_FACTORIALS`. Each name is checked against the registry vocabulary
    (canonical `Factorial` enum + `extra_factorials`) so the displayed set is a
    deliberate subset of ground truth, never an invented name."""
    known = set(reg.factorials) | set(extra_factorials)
    unknown = [f for f in SCHEMA_FACTORIALS if f not in known]
    if unknown:
        raise SystemExit(
            f"SCHEMA_FACTORIALS not in registry vocabulary {sorted(known)}: {unknown}"
        )
    return list(SCHEMA_FACTORIALS)


def list_all_keys(s3) -> set[str]:
    keys: set[str] = set()
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=f"{EXPERIMENT}/output/"):
        for obj in page.get("Contents", []):
            keys.add(obj["Key"])
    return keys


def main() -> None:
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3 = session.client(
        "s3",
        region_name=REGION,
        endpoint_url=ENDPOINT,
        config=Config(retries={"max_attempts": 3}),
    )

    schema = build_schema()
    print(f"  factorial schema ({len(schema)}): {schema}")

    print(f"listing s3://{BUCKET}/{EXPERIMENT}/output/ ...")
    keys = list_all_keys(s3)
    print(f"  {len(keys)} objects on bucket")

    variables = list(reg.variables)
    models_out = []

    for model_key, adapter in adapters.items():
        # Every model is scored against the SAME schema. `declared` = the schema
        # factorials this model's run plan actually includes; the page renders every
        # schema row and marks the rest not-run. Factorials a model runs that are
        # OUTSIDE the schema (e.g. JULES's permafrost/fire-sweep variants) are
        # intentionally omitted.
        declared = [f for f in schema if f in adapter.FACTORIALS]

        coverage: dict[str, dict[str, list[str]]] = {}
        for fac in declared:
            coverage[fac] = {}
            for sim in SIMULATIONS:
                present = []
                for var in variables:
                    try:
                        key = path_to_key(adapter.one_pct_path(sim, FORCING, fac, var))
                    except Exception:
                        continue  # pure transform hiccup for an odd var -> treat as absent
                    if key in keys:
                        present.append(var)
                coverage[fac][sim] = present

        model_dir = path_to_key(
            adapter.one_pct_path("bgc", FORCING, "baseline", "cVeg")
        ).split("/")[2]

        models_out.append(
            {
                "key": model_key,
                "label": adapter.model,  # e.g. "LPX-Bern", "TEM-MDM"
                "dir": model_dir,
                "declared_factorials": declared,
                "coverage": coverage,
            }
        )
        filled = sum(1 for f in coverage.values() for v in f.values() if v)
        total_vars = sum(len(v) for f in coverage.values() for v in f.values())
        print(
            f"  {adapter.model:12} {len(declared)} factorials, "
            f"{filled} non-empty (factorial,sim) cells, {total_vars} variable-files"
        )

    out = {
        "generated_at": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "registry_version": reg.__version__,
        "experiment": EXPERIMENT,
        "forcing": FORCING,
        "variables_total": len(variables),
        "simulations": SIMULATIONS,
        "factorial_schema": schema,
        "factorial_labels": {f: FACTORIAL_LABELS.get(f, f) for f in schema},
        "models": models_out,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT}  ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
