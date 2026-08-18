Title: WIEMIP · Quickstart
Nav: Quickstart
Description:

<!-- Deliberately code-first: the blocks are the documentation, the headings are the
     index. Add a sentence anywhere you think a newcomer needs one. -->

# Quickstart

```python
import wiemip_registry as wr
```

## Ask for a variable

```python
# 1pctCO2: model, GCM pattern, run, factorial, variable
cveg = wr.retrieve_one_pct_variable(
    model="CLASSIC", forcing="ukesm", simulation="cou",
    factorial="baseline", variable="cVeg",
)

# overshoot: no factorial (except JULES, which ran the scenarios under fire configs)
hl = wr.retrieve_overshoot_variable(
    model="LPX_Bern", forcing="ukesm", simulation="hl", variable="cVeg",
)
```

Both return a `WIEFile`. Nothing is read from the bucket yet.

<!-- Worth a line here on the stable-vs-GCM-pattern rule, or a link to Overview. -->

## `.path` — which file is this?

```python
cveg.path
# '/mnt/wiemip/1pctCO2/output/CLASSIC/CLASSIC_UKESM_1pctCO2-COU/…_cVeg_ann_1deg.nc'
```

Pure name transform, no disk access. First thing to print when a number looks wrong.

## `.exists()` — is it actually there?

```python
cveg.exists()          # True / False, never raises
```

```python
# safe to sweep the whole product with this
for model in wr.models:
    f = wr.retrieve_one_pct_variable(
        model=model, forcing="ukesm", simulation="cou",
        factorial="baseline", variable="cVeg",
    )
    print(f"{model:12s} {f.exists()}")
```

## `.read()` — the gridded field

```python
data = cveg.read()     # xarray.DataArray; raises FileNotFoundError if not uploaded

data.dims              # ('time', 'lat', 'lon'), plus any extra dims
data.time              # datetime64[us], at the file's own cadence
cveg.units             # units string from the file header
cveg.kind              # 'stock' or 'flux'
```

Dims renamed, time decoded, sentinel fills masked to `NaN`. **Units stay as the model
wrote them** — conversion happens in `latitudinal_sum()`.

## `.latitudinal_sum()` — global and regional totals

```python
series = cveg.latitudinal_sum()             # whole globe, Pg C (or Pg C/yr for a flux)
tropics = cveg.latitudinal_sum(-30, 30)     # a latitude band
fresh = cveg.latitudinal_sum(overwrite=True)  # ignore the cached CSV and recompute
```

Returns a `pandas.Series` at the file's native cadence. Cached to CSV, keyed on the
source `.nc` mtime.

## `.weighted_dataarray()` — your own arithmetic

```python
weighted = cveg.weighted_dataarray()        # area weights applied, nothing summed yet
weighted.mean(("lat", "lon"))               # area-weighted global mean
weighted.sum(("lat", "lon"))                # unconverted total

change = data.isel(time=-1) - data.isel(time=0)
change.plot()                               # a map
```

## Totals across pools

```python
wr.land_carbon_variables("CLASSIC")   # which pools this model reports
wr.land_carbon_stock(
    experiment="1pctCO2", model="CLASSIC", forcing="ukesm",
    simulation="cou", factorial="baseline",
)                                     # their sum, Pg C
```

## What's valid

```python
wr.models                     # registered models
wr.gcm_patterns               # ukesm / ipsl / gfdl / stable
wr.one_percent_simulations    # bgc, cou, ctrl, rad (+ _ndep variants)
wr.overshoot_simulations      # hist, l, hl, hl_cf, m, …
wr.variables                  # CMIP short names
wr.factorials                 # the shared factorial names
wr.adapters["CLASSIC"].factorials   # what one model actually declares
```

## When it raises

```python
from wiemip_registry.core import (
    MissingModelError, MissingForcingError, MissingSimulationError,
    MissingVariableError, MissingFactorialError, InvalidSimulationError,
)
```

| raised at | why |
| --- | --- |
| request time | the name isn't in a vocabulary, or the model has no such factorial |
| `InvalidSimulationError` | the combination isn't in the protocol (`bgc` + `ukesm`) |
| `.read()` | valid request, file was never uploaded (`FileNotFoundError`) |

## Helpers in `core`

<!-- These are for adapter authors more than for analysts — trim if that's the wrong
     audience for this page. -->

```python
from wiemip_registry import core

core.kind_of("cVeg")          # 'stock' vs 'flux' — picks the unit conversion
core.is_annual("cVeg")        # cadence token: yr/ann vs mon
core.spherical_area(ds, "lat", "lon")   # cell area [m2] when no raster was shipped
core.mask_fill(da)            # sentinel fills -> NaN
core.rename_latlon(da, "latitude", "longitude")   # -> canonical lat/lon
core.standardize(da, "lat", "lon", time)          # canonical dims + time coord
core.to_datetime64(values)    # -> datetime64[us] (ns overflows past 2262)
core.years_to_datetime(vals)  # numeric/fractional years -> datetime64
```
