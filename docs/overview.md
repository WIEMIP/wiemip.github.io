Title: WIEMIP · wiemip_registry docs
Nav: Overview
Description:

<!-- Cues are HTML comments: invisible on the page, though still in the HTML source.
     Delete as you go. Headings render with nothing under them, so the page is safe to
     publish half-finished. -->

# Overview

<!-- 2-3 sentences: what wiemip_registry is, for someone who has never used it. -->

## What problem this solves

<!-- Every group uploads differently; this gives one way to ask for a variable.
     Worth saying why that matters before the how. -->

## Who this is for

<!-- Modelling groups checking their own submission? Anyone doing cross-model
     analysis? Says who should read on. -->

## Where it runs

### On the JupyterHub

<!-- Pre-installed, bucket already mounted, cache already warm. -->

### On your own machine

<!-- Clone + uv sync; WIEMIP_DATA_ROOT and WIEMIP_CSV_PATH; the
     set-it-before-you-import gotcha. -->

### Colab and other hosted notebooks

<!-- pip not uv sync; mount it yourself; credentials warning; expect it slow. -->

## Quick start

<!-- Shortest thing that works: one request, .path, .read(), .latitudinal_sum(). -->

## What goes into a request

<!-- The five axes and how to list the valid values for each. A table works here. -->

### Which forcing goes with which simulation

<!-- The stable-vs-GCM-pattern rule, and what happens if you get it wrong. -->

## The simulations

<!-- 1pctCO2 vs overshoot run names. What _ndep and _cf mean. Which models have
     actually uploaded overshoot output. -->
