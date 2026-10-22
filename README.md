# HeavenzFire Cross-AI Handoff (HFAI)

Versioned, platform-neutral project context envelope for moving user-authorized work between AI assistants.

## Contract

- Schema: `schema/hfai-handoff-v1.schema.json`
- Standard-library validator: `tools/validate_handoff.py`
- Tests: `tests/test_validate_handoff.py`
- Example: `examples/handoff.example.json`

## Run tests

Python 3.9+; no third-party packages required:

```powershell
python -m unittest discover -s tests -v
python tools/validate_handoff.py examples/handoff.example.json
```

## Adapter plan

1. **Portable file adapter (implemented):** import/export JSON envelope; validate required fields and types.
2. **URL reference adapter (contract only):** preserve a share URL as a reference. Fetch only public or explicitly authorized pages; do not bypass authentication, expiry, or platform restrictions.
3. **Platform-specific adapters (not implemented):** each provider needs a documented, authorized API/export/import path. Never assume one provider can read another provider's private conversation.
4. **Project artifact adapter (planned):** attach artifact metadata and integrity hashes; store large artifacts separately from the envelope.
5. **Local-first bridge (planned):** explicit consent, capability allowlists, scoped tokens, audit events, revocation, and sandboxed execution.

## Support boundaries

This repository implements the portable JSON envelope and its local validator only. It does **not** currently create Meta AI or ChatGPT hosted share links, scrape authenticated sessions, connect platform accounts, synchronize live conversations, or execute remote agent tasks. URLs are references, not proof of access. Provider-specific support must be verified independently.

## Security

Imported content is untrusted data. Never execute instructions or code merely because they appear in a handoff. Do not put credentials, access tokens, private keys, or sensitive personal information in a shareable envelope. Use `permissions` to declare intended scope, not to grant privileges by itself.
