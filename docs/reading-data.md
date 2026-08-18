Title: WIEMIP · Reading data
Nav: Reading data
Description:

# Reading data

<!-- One or two lines: a request hands back a WIEFile, and nothing is read until
     you ask for data. -->

## What a request gives you

<!-- The members worth knowing: .path, .exists(), .read(), .weighted_dataarray(),
     .latitudinal_sum(), .units, .kind. Table is probably clearest. -->

### Why .path never fails and .read() does

<!-- The design split, and what it buys you when a number looks wrong. -->

## The gridded field

<!-- What read() standardizes: dim names, time decoding, fill masking. And that
     units stay as the model wrote them. -->

## Global and regional totals

<!-- latitudinal_sum(), with and without a band. -->

### Units

<!-- Stocks vs fluxes, and what the returned numbers are in. -->

### Monthly vs annual

<!-- Native cadence is preserved; nothing is silently averaged. -->

### Area weighting

<!-- Provided rasters vs computed spherical area; masked cells drop out. -->

## The CSV cache

<!-- Where it lives, that it's shared on the hub, what invalidates it, and how to
     force a recompute. -->

## Total land carbon

<!-- land_carbon_variables() / land_carbon_stock(), and that the pool list differs
     between models. -->

## When something errors

<!-- The exception list and what each one means. Which fire at request time vs on
     read. -->
