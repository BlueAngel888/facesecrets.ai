---
name: RevenueCat store isolation
description: Why the mobile purchase verifier distinguishes Test Store from native store products
---

Require a server-verified purchase from the correct RevenueCat app for the current environment, not merely a matching store product identifier. Test Store reports are development-only.

**Why:** One RevenueCat offering can contain Test Store, Apple, and Google products with the same store identifier. Checking only that identifier would allow a free test transaction to fund a production report.

**How to apply:** When changing products, offerings, purchase bridges, or redemption, preserve independent app/environment verification on the server and tests for both test and native purchases. Never authorize a report from a client entitlement claim alone.