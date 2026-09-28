---
name: Security override compatibility
description: Runtime compatibility checks needed when security overrides jump module formats.
---

When an audit fix forces a transitive package across a CommonJS-to-ESM boundary, test the immediate parent package's actual API at runtime, not just compilation or a successful audit. A major-version bump of that parent may also break its own CommonJS consumers.

**Why:** A patched decoder exported an ESM default where its older CommonJS parent expected a callable `require`; updating the parent to its ESM release then exposed another CommonJS interop mismatch. Both changes passed typechecking and bundling while breaking query handling.

**How to apply:** Smoke-test the dependency chain's actual parse/stringify or equivalent operations. Prefer a narrow, documented compatibility patch over an untested major-version override when the parent has no compatible upstream release in the current dependency chain.