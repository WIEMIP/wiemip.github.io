#!/usr/bin/env python3
"""
Coverage reader for the WIEMIP progress page: the FULL legal request product, spelled
through the registry, checked against what is actually on the bucket.

For every registered model x experiment x factorial x simulation x GCM pattern x
variable the registry can name, this asks the adapter which file(s) it would open and
counts the variable as uploaded iff every one of those files is on the bucket. Nothing
is hand-picked: the simulations are `wr.one_percent_simulations` /
`wr.overshoot_simulations`, the factorials are the adapter's own `FACTORIALS` /
`OVERSHOOT_FACTORIALS`, the variables are `wr.variables`, and the pattern each
simulation may be requested under follows `core.ensure_valid` (constant-climate runs
under `stable`, transient ones under the three GCMs). Same generator as
debug/test_wr.py's coverage phase in the registry repo.

Two ways to run it. Same output either way.

  1. From the laptop, off a bucket listing (no box, no mount needed; a few seconds):

        AWS_PROFILE=wasabi-read-only aws s3 ls s3://wiemip/ --recursive \
            --endpoint-url https://s3.us-east-2.wasabisys.com > /tmp/bucket_listing.txt
        uv run --project ~/projects/wiemip-data-processing \
            python tools/progress_coverage.py --listing /tmp/bucket_listing.txt > coverage.json

  2. ON the wiemip-hub box (bucket mounted at /mnt/wiemip), under the TLJH python:

        /opt/tljh/user/bin/python tools/progress_coverage.py > coverage.json

Model dirs with no registry adapter (BiomeE, the empty placeholders, a brand-new group)
are scanned coarsely: files carrying an ESM token in the name, per experiment. Enough to
light up the moment they upload, before someone writes their adapter.

Emits raw per-run variable counts as JSON on stdout; tools/build_progress.py turns them
into status dots and writes progress/data.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import wiemip_registry as wr
from wiemip_registry.adapters import adapters
from wiemip_registry.const import DATA_ROOT

GCM_FORCINGS = ["ukesm", "ipsl", "gfdl"]  # the three ESM driver patterns
CONSTANT_CLIMATE_FORCING = "stable"       # what bgc / ctrl (and their _ndep twins) are requested under
EXPERIMENTS = {"1pctCO2": DATA_ROOT / "1pctCO2" / "output", "overshoot": DATA_ROOT / "overshoot" / "output"}
IGNORE_DIRS = {"extremes"}  # dirs under <exp>/output/ that are not a model
# Groups dropped from the tracker (not participating); their bucket dirs, if any, are skipped.
DROPPED_DIRS = {"UVIC", "CoLM", "GDSTEM", "KG-FM", "IBIS", "ModelE-SLSM", "VISIT-NIES"}
# Bucket dir -> tracker key, where `dir.replace("-", "_")` is not the key build_progress
# uses for POC / planned-factorial lookup.
KEY_FOR_DIR = {"ORCHIDEE-MICT-CALIPSO": "ORCHIDEE_MICT"}


def legal_forcings(experiment: str, simulation: str) -> list[str]:
    """The patterns a simulation may be requested under. 1pctCO2: cou/rad (and their
    _ndep twins) are driven by a transient GCM pattern; bgc/ctrl hold the climate
    constant and `core.ensure_valid` only admits `stable` for them (ctrl_ndep is
    ungated in the code but is a constant-climate run by protocol, so it is treated
    the same). Overshoot: every scenario under every GCM; hist/ctrl carry no pattern
    for most groups and simply resolve to the same files under each."""
    if experiment == "overshoot":
        return GCM_FORCINGS
    return GCM_FORCINGS if simulation.split("_")[0] in ("cou", "rad") else [CONSTANT_CLIMATE_FORCING]


def request_grid(experiment: str) -> list[list[str]]:
    """Every legal (simulation, forcing) column of the product, in namespace order."""
    sims = wr.overshoot_simulations if experiment == "overshoot" else wr.one_percent_simulations
    return [[s, f] for s in sims for f in legal_forcings(experiment, s)]


# --- what is on the bucket ---------------------------------------------------------

def load_listing(listing: Path) -> set[str]:
    """Every .nc key from an `aws s3 ls --recursive` dump, spelled as the /mnt/wiemip
    path the adapters build (`<date> <time> <size> <key>` per line)."""
    present = set()
    with open(listing) as fh:
        for line in fh:
            parts = line.rstrip("\n").split(None, 3)
            if len(parts) == 4 and parts[3].endswith(".nc"):
                present.add(str(DATA_ROOT / parts[3]))
    return present


def model_dirs_in_listing(listing: Path) -> set[str]:
    """Every `<exp>/output/<dir>` name in the dump, including the zero-byte placeholder
    keys the empty groups have, so a model with nothing uploaded still gets a row."""
    dirs = set()
    with open(listing) as fh:
        for line in fh:
            parts = line.rstrip("\n").split(None, 3)
            if len(parts) != 4:
                continue
            bits = parts[3].split("/")
            if len(bits) >= 3 and bits[1] == "output" and bits[0] in EXPERIMENTS and bits[2]:
                dirs.add(bits[2])
    return dirs


class Bucket:
    """Answers "which .nc files sit under this dir": from the listing when given one,
    from the s3fs mount otherwise."""

    def __init__(self, listing: Path | None):
        self.listing = listing
        self._all = load_listing(listing) if listing else None

    def present_nc(self, directory: Path) -> set[str]:
        if self._all is not None:
            prefix = str(directory) + "/"
            return {p for p in self._all if p.startswith(prefix)}
        if not directory.is_dir():
            return set()
        return {str(p) for p in directory.rglob("*.nc")}

    def model_dirs(self) -> set[str]:
        if self.listing is not None:
            return model_dirs_in_listing(self.listing)
        dirs = set()
        for root in EXPERIMENTS.values():
            if root.is_dir():
                dirs.update(p.name for p in root.iterdir() if p.is_dir())
        return dirs


# --- registered models: the full product -------------------------------------------------

def dir_name(model: str) -> str:
    """The model's on-disk dir name (alias != dir, e.g. LPX_Bern -> LPX-Bern), derived
    from a sample 1pct path so it tracks the adapter. Same dir in both experiments."""
    sample = wr.retrieve_one_pct_variable(model, "ukesm", "cou", "baseline", "cVeg").path
    parts = Path(sample).parts
    return parts[parts.index("output") + 1]


def product_coverage(model: str, adapter, bucket: Bucket, variables: list[str]) -> dict:
    """One row per (experiment, factorial, simulation, forcing) with at least one
    variable on the bucket: {"factorial", "simulation", "forcing", "vars"}. `vars`
    counts requested variables whose every file (CLM chunks, pool splits) is present."""
    d = dir_name(model)
    out = {"key": model, "label": adapter.model, "dir": d, "runs": {}, "mapped": {}, "factorials": {}, "files": {}}
    for experiment, root in EXPERIMENTS.items():
        present = bucket.present_nc(root / d)
        out["files"][experiment] = len(present)
        if experiment == "1pctCO2":
            factorials = list(adapter.FACTORIALS)
            sims = list(wr.one_percent_simulations)

            def retrieve(fac, sim, forcing, var):
                return wr.retrieve_one_pct_variable(model, forcing, sim, fac, var)
        else:
            factorials = list(adapter.OVERSHOOT_FACTORIALS) or [None]
            sims = list(wr.overshoot_simulations)

            def retrieve(fac, sim, forcing, var):
                return wr.retrieve_overshoot_variable(model, forcing, sim, var, fac)

        out["factorials"][experiment] = [f for f in factorials if f is not None]
        rows, mapped = [], True
        for fac in factorials:
            for sim in sims:
                for forcing in legal_forcings(experiment, sim):
                    n = 0
                    for var in variables:
                        try:
                            paths = retrieve(fac, sim, forcing, var).paths
                        except NotImplementedError:  # no overshoot grammar for this model
                            mapped = False
                            break
                        except Exception:  # a factorial/variable this adapter cannot spell
                            continue
                        if paths and all(p in present for p in paths):
                            n += 1
                    if not mapped:
                        break
                    if n:
                        rows.append({"factorial": fac or "baseline", "simulation": sim, "forcing": forcing, "vars": n})
                if not mapped:
                    break
            if not mapped:
                break
        out["runs"][experiment] = rows
        out["mapped"][experiment] = mapped
    return out


# --- no adapter: coarse ESM-token scan --------------------------------------------------

def coarse_coverage(d: str, bucket: Bucket) -> dict:
    """No adapter: attribute files to a driver by the ESM token in the filename (only
    the pattern-forced runs carry one) and count the untagged rest. Coarse but real."""
    out = {"key": KEY_FOR_DIR.get(d, d.replace("-", "_")), "dir": d, "coarse": {}, "files": {}}
    for experiment, root in EXPERIMENTS.items():
        present = bucket.present_nc(root / d)
        tagged = {f: sum(1 for p in present if f in Path(p).name.lower()) for f in GCM_FORCINGS}
        tagged["untagged"] = len(present) - sum(tagged.values())
        out["coarse"][experiment] = tagged
        out["files"][experiment] = len(present)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="WIEMIP bucket coverage -> JSON on stdout")
    ap.add_argument("--listing", type=Path, default=None,
                    help="`aws s3 ls s3://wiemip/ --recursive` dump; omit on the box (reads the mount)")
    args = ap.parse_args()
    bucket = Bucket(args.listing)

    variables = list(wr.variables)
    models = []
    for key, adapter in adapters.items():
        print(f"  {key}", file=sys.stderr)
        models.append(product_coverage(key, adapter, bucket, variables))
    registered_dirs = {m["dir"] for m in models}
    unregistered = [
        coarse_coverage(d, bucket)
        for d in sorted(bucket.model_dirs() - registered_dirs - IGNORE_DIRS - DROPPED_DIRS, key=str.lower)
    ]

    print(
        json.dumps(
            {
                "registry_version": wr.__version__,
                "variables_total": len(variables),
                "gcm_forcings": GCM_FORCINGS,
                "constant_climate_forcing": CONSTANT_CLIMATE_FORCING,
                "experiments": {exp: {"grid": request_grid(exp)} for exp in EXPERIMENTS},
                "models": models,
                "unregistered": unregistered,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
