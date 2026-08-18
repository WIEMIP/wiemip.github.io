Title: WIEMIP · Adding a model
Nav: Adding a model
Description:

# Adding a model

<!-- One or two lines: a model joins by contributing one adapter; everything else
     is already generic. -->

## What you need first

<!-- The real bucket listing for that model, and its README (area recipe, fills).
     Naming comes from what was uploaded, not from the protocol. -->

## The steps

<!-- Numbered: copy a template dir, work out the grammar, implement the hooks,
     declare FACTORIALS + land_carbon_variables, register in adapters.py. -->

## A minimal adapter

<!-- Code block. LPJ_EOSIM is the smallest real one to model it on. -->

## Rules that keep adapters interchangeable

<!-- path() is a pure transform; read() is the existence gate; spell the requested
     forcing; units stay native. Each of these exists because breaking it caused a
     silent wrong-data bug — worth saying which. -->

## Helpers you don't have to write

<!-- The core.py utilities. -->

## Things that vary more than you'd expect

<!-- Coord names and dim order, time encoding, cadence tokens, area, fills. -->

## Checking it against the bucket

<!-- The debug/ harnesses, what "uncovered" means, and when the adapter is done. -->

## Contributing it

<!-- PR, and that a push to main syncs the hub environment. -->
