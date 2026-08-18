# pdoc template overrides

Used by `docs/build_api.sh` via `--template-directory`. pdoc checks this directory
before falling back to its own defaults (`default/*.jinja2`), so each file here only
needs to override what actually differs.

- `custom.css` — pdoc's own override slot (empty by default upstream). Shrinks the
  project logo to a small top-left mark instead of the full-width banner its default
  CSS produces.
- `module.html.jinja2` — reorders the sidebar so "API Documentation" comes before
  "Submodules". Extends the default template and replays every nav sub-block in a
  different order; nothing else changes.

Re-run `bash docs/build_api.sh` after editing either file.
