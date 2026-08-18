Title: WIEMIP · Factorials
Nav: Factorials
Description:

# Factorials

<!-- Plain-language definition first: a run with a process switched off. -->

## Why WIEMIP asks for them

<!-- The science reason — isolating a process's contribution to the feedback
     factors. This is the bit a newcomer won't get from the code. -->

## Factorials are per model

<!-- Each adapter declares its own list; how to check what a given model has. -->

### The shared names

<!-- const.Factorial. -->

### Model-specific names

<!-- const.extra_factorials; passing one as a plain string. -->

## Baseline vs factorial

<!-- What counts as the baseline, and that _ndep is a simulation not a factorial. -->

## Comparing them properly

<!-- Difference against the same model's own baseline, then compare differences
     across models. Worth being explicit about. -->

## Asking for one a model doesn't have

<!-- What raises, what returns False, and how to sweep the whole product safely. -->

## Naming quirks

<!-- Optional: the per-model spelling table, if it's useful to have here rather
     than in AGENTS.md. -->
