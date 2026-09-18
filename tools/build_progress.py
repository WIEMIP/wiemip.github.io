#!/usr/bin/env python3
"""
Regenerate progress-tracker/data.json, the data behind https://wiemip.github.io/progress-tracker/.
Runs nightly in .github/workflows/progress.yml; run it by hand after an upload you want to see now.

    python3 tools/build_progress.py --listing /tmp/bucket_listing.txt   # from the laptop (preferred)
    python3 tools/build_progress.py                                     # SSH to the box, live
    python3 tools/build_progress.py --coverage f.json                   # from a saved coverage.json

The --listing route needs no box at all: dump the bucket with
    AWS_PROFILE=wasabi-read-only aws s3 ls s3://wiemip/ --recursive \
        --endpoint-url https://s3.us-east-2.wasabisys.com > /tmp/bucket_listing.txt
and the coverage reader (tools/progress_coverage.py) runs in this interpreter when
`wiemip_registry` is importable (CI), else under the registry repo's venv
($WIEMIP_REGISTRY_REPO, default ~/projects/wiemip-data-processing) via `uv run`.

Ground truth is the full legal request product -- every experiment x factorial x
simulation x GCM pattern x variable the registry can name -- checked against the bucket.
This script only DERIVES colours from those per-run variable counts; it never decides
what exists. The rules, applied per model with `reference` = the model's fullest run in
that experiment (its max variable count over every run):

  * a run is COMPLETE at >= COMPLETE_SHARE x reference variables, PARTIAL below that,
    ABSENT at zero. (Catches a run whose upload stopped half way, like CLM's ipsl M.)
  * a dot summarises a set of required runs: green = all complete, amber = something is
    there but a run is missing or partial, red = nothing.
      1pctCO2  ctrl+bgc column   -> {ctrl, bgc} under `stable`, baseline factorial
      1pctCO2  UKESM/IPSL/GFDL   -> {cou} under that pattern, baseline factorial
      overshoot, one dot per scenario -> that scenario under all three GCM patterns
        (the hover lists ukesm / ipsl / gfdl); hist / hist_ctrl / ctrl carry no pattern
        token, so their colour is the best pattern. The per-GCM {l, hl, hl_cf, m}
        summaries are still computed for the hero stats.
  * a factorial chip is the same rule over that factorial's {ctrl, bgc, cou x 3};
    grey when the adapter declares it but nothing is uploaded. The chips ARE the
    adapter's `FACTORIALS` -- nothing is filtered or relabelled here.
  * rad, the _ndep twins and the optional overshoot scenarios never colour a dot; they
    are listed in the tooltips and the expandable run grid.

The only hand-set fields are POC (a human to chase) and the planned factorials of groups
that have no adapter yet (no bucket data to derive them from).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

# --- edit me ---------------------------------------------------------------
SITE_ROOT = Path(__file__).resolve().parent.parent
COVERAGE_SCRIPT = SITE_ROOT / "tools" / "progress_coverage.py"
OUT = SITE_ROOT / "progress-tracker" / "data.json"
BOX = os.environ.get("WIEMIP_BOX", "wiemip-hub")
BOX_PYTHON = "/opt/tljh/user/bin/python"
# The registry checkout whose venv runs the coverage reader in --listing mode.
REGISTRY_REPO = Path(os.environ.get("WIEMIP_REGISTRY_REPO", "~/projects/wiemip-data-processing")).expanduser()

# A run counts as complete at this share of the model's fullest run in the experiment.
COMPLETE_SHARE = 0.8
# The runs each dot summarises (simulation, forcing); "<gcm>" is the column's pattern.
ONE_PCT_CONSTANT = [("ctrl", "stable"), ("bgc", "stable")]
ONE_PCT_DRIVER = [("cou", "<gcm>")]
OVERSHOOT_REQUIRED = [("l", "<gcm>"), ("hl", "<gcm>"), ("hl_cf", "<gcm>"), ("m", "<gcm>")]
FACTORIAL_REQUIRED = ONE_PCT_CONSTANT + [("cou", g) for g in ("ukesm", "ipsl", "gfdl")]
# Overshoot scenarios in protocol reading order (history + controls, then low -> high),
# which ones the protocol requires, and which carry no GCM pattern (CRUJRA-driven).
SCENARIO_ORDER = ["hist", "ctrl", "vl", "vl_cf", "l", "m", "ml", "ml_cf", "hl", "hl_cf"]
SCENARIOS_REQUIRED = {"hist", "l", "hl", "hl_cf", "m"}
SCENARIOS_PATTERNLESS = {"hist", "ctrl"}
# The registry spells the overshoot control two ways (LPJ-EOSIM uploaded `hist_ctrl`,
# everyone else `ctrl`); it is one simulation, so the page folds them into one column.
SCENARIO_ALIASES = {"hist_ctrl": "ctrl"}

# Planned factorial runs for groups with NO adapter (nothing on the bucket to derive
# them from) -- from the tracking spreadsheet. Shown as grey "planned" chips.
PLANNED_FACTORIALS = {
    "BiomeE": ["noFire", "noNitrogen"],
    "ELM": [],
    "ORCHIDEE_MICT": ["noPermafrost", "noWetland"],
    "IBIS": ["noFire", "noWetland"],
    "CARDAMOM_JPL": ["noFire"],
}

# Point of contact per model: a human to chase, not derivable from the bucket.
POC = {
    "LPX_Bern": "Hyuna Kim",
    "DLEM": "Susan Pan / Yuchun Zhang",
    "CLASSIC": "Vivek Arora / Sal Curasi",
    "VISIT_UT": "Akihiko Ito",
    "CLM_FATES": "Rosie Fisher",
    "JULES": "Eleanor Burke",
    "LPJ_EOSIM": "Tom Colligan",
    "TEM": "Shuo Chen / Qianlai Zhuang",
    "BiomeE": "Paul Lerner",
    "JSBACH": "Beiyao Xu",
    "LPJmL6": "Sibyll Schaphoff",
    "CLM": "Will Wieder",
    "LPJ_GUESS": "Prashant Paudel / Benjamin Smith",
    "ELM": "Qing Zhu",
    "DVM_DOS_TEM": "Elchin Jafarov / Helene Genet",
    "ORCHIDEE_MICT": "Yi Xi / Julien Alléon",
    "BEPS": "Mousong Wu",
    "IBIS": "Min Chen",
    "CARDAMOM_JPL": "Eren Bilir",
}
# ---------------------------------------------------------------------------


def fetch_coverage_from_box() -> dict:
    """Run tools/progress_coverage.py on the box under its TLJH python and parse the
    JSON it prints. The script is piped over stdin so nothing is copied to the box."""
    print(f"running coverage reader on {BOX} ...", file=sys.stderr)
    proc = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=30", BOX, f"{BOX_PYTHON} -"],
        stdin=COVERAGE_SCRIPT.open("rb"),
        capture_output=True,
    )
    if proc.returncode != 0:
        sys.exit(f"coverage reader failed on {BOX} (exit {proc.returncode}):\n" + proc.stderr.decode(errors="replace"))
    return json.loads(proc.stdout)


def fetch_coverage_from_listing(listing: Path) -> dict:
    """Run tools/progress_coverage.py locally, under the registry repo's venv, off an
    `aws s3 ls --recursive` dump. No box involved."""
    print(f"running coverage reader locally on {listing} ...", file=sys.stderr)
    try:  # CI installs wiemip_registry into this interpreter; on the laptop it lives in the registry repo's venv
        import wiemip_registry  # noqa: F401
        cmd = [sys.executable, str(COVERAGE_SCRIPT), "--listing", str(listing)]
    except ImportError:
        cmd = ["uv", "run", "--project", str(REGISTRY_REPO), "python", str(COVERAGE_SCRIPT), "--listing", str(listing)]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        sys.exit(f"coverage reader failed (exit {proc.returncode}):\n" + proc.stderr.decode(errors="replace"))
    return json.loads(proc.stdout)


# --- deriving colours from the product ---------------------------------------------------

def run_state(vars_present: int, reference: int) -> str:
    if vars_present <= 0:
        return "absent"
    return "complete" if reference and vars_present >= COMPLETE_SHARE * reference else "partial"


def summarise(required: list[tuple[str, str]], gcm: str | None, lookup: dict, reference: int) -> dict:
    """Colour for a set of required (simulation, forcing) runs of one factorial.
    `lookup` maps (simulation, forcing) -> variable count. "<gcm>" is filled from `gcm`;
    "any" takes the best count over the three patterns (hist has no pattern token)."""
    runs = []
    for sim, forcing in required:
        forcing = gcm if forcing == "<gcm>" else forcing
        if forcing == "any":
            n = max((lookup.get((sim, f), 0) for f in ("ukesm", "ipsl", "gfdl")), default=0)
            forcing = "any pattern"
        else:
            n = lookup.get((sim, forcing), 0)
        runs.append({"simulation": sim, "forcing": forcing, "vars": n, "state": run_state(n, reference)})
    states = [r["state"] for r in runs]
    if all(s == "complete" for s in states):
        status = "green"
    elif any(s != "absent" for s in states):
        status = "yellow"
    else:
        status = "red"
    return {"status": status, "runs": runs}


def fold_aliases(rows: list[dict]) -> list[dict]:
    """Rename aliased simulations and merge duplicates (max variables -- a group uploads
    one spelling or the other, and if both they are the same files)."""
    merged: dict[tuple, dict] = {}
    for r in rows:
        r = dict(r, simulation=SCENARIO_ALIASES.get(r["simulation"], r["simulation"]))
        key = (r["factorial"], r["simulation"], r["forcing"])
        if key not in merged or r["vars"] > merged[key]["vars"]:
            merged[key] = r
    return list(merged.values())


def registered_model(cm: dict, forcings: list[str]) -> dict:
    """Everything the page shows for one registered model, derived from its runs."""
    runs = dict(cm["runs"])
    runs["overshoot"] = fold_aliases(runs.get("overshoot", []))
    reference = {exp: max((r["vars"] for r in rows), default=0) for exp, rows in runs.items()}

    def lookup(exp: str, factorial: str) -> dict:
        return {(r["simulation"], r["forcing"]): r["vars"] for r in runs[exp] if r["factorial"] == factorial}

    one = lookup("1pctCO2", "baseline")
    over = lookup("overshoot", "baseline")
    status = {
        "1pctCO2": {"constant": summarise(ONE_PCT_CONSTANT, None, one, reference["1pctCO2"])},
        "overshoot": {"hist": summarise([("hist", "any")], None, over, reference["overshoot"])},
    }
    for g in forcings:
        status["1pctCO2"][g] = summarise(ONE_PCT_DRIVER, g, one, reference["1pctCO2"])
        status["overshoot"][g] = summarise(OVERSHOOT_REQUIRED, g, over, reference["overshoot"])

    scenarios = []
    for sim in sorted({r["simulation"] for r in runs["overshoot"]} | set(SCENARIO_ORDER),
                      key=lambda x: (SCENARIO_ORDER.index(x) if x in SCENARIO_ORDER else 99, x)):
        per_gcm = summarise([(sim, g) for g in forcings], None, over, reference["overshoot"])
        # hist / hist_ctrl / ctrl carry no pattern token, so their colour is the best pattern;
        # the hover still lists all three so a one-pattern upload (LPX-Bern hist) is visible.
        colour = summarise([(sim, "any")], None, over, reference["overshoot"])["status"] if sim in SCENARIOS_PATTERNLESS else per_gcm["status"]
        scenarios.append({"name": sim, "status": colour, "runs": per_gcm["runs"], "required": sim in SCENARIOS_REQUIRED})
    status["overshoot"]["scenarios"] = scenarios

    chips = []
    for fac in cm["factorials"]["1pctCO2"]:
        if fac == "baseline":
            continue
        s = summarise(FACTORIAL_REQUIRED, None, lookup("1pctCO2", fac), reference["1pctCO2"])
        chips.append({"name": fac, "status": "gray" if s["status"] == "red" else s["status"], "runs": s["runs"]})

    return {
        "key": cm["key"],
        "label": cm["label"],
        "dir": cm["dir"],
        "registered": True,
        "empty": sum(cm["files"].values()) == 0,
        "poc": POC.get(cm["key"], "—"),
        "files": cm["files"],
        "mapped": cm["mapped"],
        "reference": reference,
        "factorials": cm["factorials"],
        "runs": runs,
        "status": status,
        "chips": chips,
    }


def unregistered_model(cm: dict, forcings: list[str]) -> dict:
    """No adapter: green/red per pattern from ESM-tagged file counts; the untagged rest
    (constant-climate runs, hist) can only be reported as "files present"."""
    status = {}
    for exp, counts in cm["coarse"].items():
        untagged = counts["untagged"]
        column = "constant" if exp == "1pctCO2" else "hist"
        status[exp] = {column: {"status": "yellow" if untagged else "red", "files": untagged}}
        for g in forcings:
            status[exp][g] = {"status": "green" if counts[g] else "red", "files": counts[g]}
    status["overshoot"]["scenarios"] = []
    return {
        "key": cm["key"],
        "label": cm["dir"],
        "dir": cm["dir"],
        "registered": False,
        "empty": sum(cm["files"].values()) == 0,
        "poc": POC.get(cm["key"], "—"),
        "files": cm["files"],
        "mapped": {exp: False for exp in cm["coarse"]},
        "reference": {},
        "factorials": {"1pctCO2": PLANNED_FACTORIALS.get(cm["key"], []), "overshoot": []},
        "runs": {},
        "status": status,
        "chips": [{"name": f, "status": "gray", "runs": []} for f in PLANNED_FACTORIALS.get(cm["key"], [])],
    }


def build(coverage: dict) -> dict:
    forcings = coverage["gcm_forcings"]
    models = [registered_model(cm, forcings) for cm in coverage["models"]]
    models += [unregistered_model(cm, forcings) for cm in coverage.get("unregistered", [])]

    # β-inputs done -> partial -> nothing; registered before unregistered within a colour.
    order = {"green": 0, "yellow": 1, "red": 2}
    models.sort(key=lambda m: (order[m["status"]["1pctCO2"]["ukesm"]["status"]], order[m["status"]["1pctCO2"]["constant"]["status"]], 0 if m["registered"] else 1, m["label"].lower()))

    def n_green(exp, columns):
        return sum(1 for m in models if all(m["status"][exp][c]["status"] == "green" for c in columns))

    stats = {
        "models": len(models),
        "registered": sum(1 for m in models if m["registered"]),
        "empty": sum(1 for m in models if m["empty"]),
        "beta_ready": n_green("1pctCO2", ["constant"]),
        "gamma_all_gcms": n_green("1pctCO2", ["constant"] + forcings),
        "overshoot_hist": n_green("overshoot", ["hist"]),
        "overshoot_all_gcms": n_green("overshoot", forcings),
    }
    experiments = coverage["experiments"]
    experiments["overshoot"]["grid"] = sorted(
        [c for c in experiments["overshoot"]["grid"] if c[0] not in SCENARIO_ALIASES],
        key=lambda c: (SCENARIO_ORDER.index(c[0]) if c[0] in SCENARIO_ORDER else 99, forcings.index(c[1]) if c[1] in forcings else 9),
    )
    experiments["overshoot"]["scenario_order"] = SCENARIO_ORDER
    experiments["overshoot"]["required"] = sorted(SCENARIOS_REQUIRED, key=SCENARIO_ORDER.index)
    experiments["overshoot"]["patternless"] = sorted(SCENARIOS_PATTERNLESS, key=SCENARIO_ORDER.index)
    experiments["overshoot"]["aliases"] = SCENARIO_ALIASES

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "registry_version": coverage["registry_version"],
        "variables_total": coverage["variables_total"],
        "gcm_forcings": forcings,
        "complete_share": COMPLETE_SHARE,
        "experiments": experiments,
        "rules": {
            "1pctCO2": {"constant": ONE_PCT_CONSTANT, "driver": ONE_PCT_DRIVER},
            "overshoot": {"hist": [["hist", "any"]], "driver": OVERSHOOT_REQUIRED},
            "factorial": FACTORIAL_REQUIRED,
        },
        "stats": stats,
        "models": models,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--coverage", type=Path, help="Build from a saved coverage.json instead of SSH-ing to the box.")
    ap.add_argument("--listing", type=Path, help="Build from an `aws s3 ls s3://wiemip/ --recursive` dump, running the coverage reader locally.")
    args = ap.parse_args()

    if args.coverage:
        coverage = json.loads(args.coverage.read_text())
    elif args.listing:
        coverage = fetch_coverage_from_listing(args.listing)
    else:
        coverage = fetch_coverage_from_box()

    out = build(coverage)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1) + "\n")

    st = out["stats"]
    print(
        f"wrote {OUT} — {st['models']} models ({st['registered']} registered, {st['empty']} empty) · "
        f"β-ready {st['beta_ready']} · γ on all GCMs {st['gamma_all_gcms']} · "
        f"overshoot hist {st['overshoot_hist']} · overshoot all GCMs {st['overshoot_all_gcms']} "
        f"(registry {out['registry_version']})"
    )


if __name__ == "__main__":
    main()
