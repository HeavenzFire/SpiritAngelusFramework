# Meta AI interchange v0.1.0 compatibility note

**Status:** received handoff text reviewed; source artifact files not attached in this ChatGPT turn, so their bytes and claimed SHA-256 values have not been independently verified.

## Findings

The pasted Meta AI envelope is a different contract from this repository's current `hfai-handoff-v1` schema (version `1.0.0`). It must not be sent unchanged to `tools/validate_handoff.py` and described as validated. The field models differ:

- Meta AI uses `version`; repository v1 uses `schema_version`.
- Meta AI models `task_status` as an array of task records; repository v1 expects one overall status string.
- Meta AI decisions are objects; repository v1 expects strings.
- Meta AI permissions use `allow_network` / `allow_code_exec` / `allow_file_write`; repository v1 requires `sharing` / `external_fetch` / `execution`.
- Artifact fields differ (`path` / `hash` vs `name` / `reference` / optional `sha256`).

## Required adapter behavior

1. Preserve the original v0.1.0 file byte-for-byte as an input artifact when supplied.
2. Parse and validate it against its own versioned schema.
3. Transform into repository v1 only through an explicit mapping function; preserve task-level status in `metadata` or a documented extension instead of silently collapsing it.
4. Map permissions conservatively: `allow_network=false` maps to `external_fetch=false`; `allow_code_exec=true` does not itself authorize remote execution; use `execution=none` unless an explicitly approved execution scope exists. Sharing must be chosen explicitly rather than inferred.
5. Recompute SHA-256 from actual bytes. Never treat the pasted abbreviated value `cfb5957e6826...` as a complete digest.
6. Emit a conversion report listing preserved, mapped, omitted, and ambiguous fields. Reject lossy conversions unless explicitly accepted.

## ChatGPT capability registry

See [the ChatGPT registry entry](../capability-registry/chatgpt.json). It describes this session's available mechanisms, not a universal guarantee about all ChatGPT clients or accounts.

## Evidence status

- Repository's existing CI run: success for the existing v1 validator tests and example-envelope validation.
- Meta AI's stated five tests: reported by the sender, not independently rerun here because `test_interchange.py` and the complete v0.1.0 schema/example/log files were not attached.
- No claim is made that the Meta AI interchange instance has been validated against either schema.
