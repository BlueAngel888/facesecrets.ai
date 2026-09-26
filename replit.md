# Ancient Wisdom

Ancient Wisdom provides private portrait-reflection reports on the web and in a separate iOS/Android Expo app.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the Flask API server
- `pnpm --filter @workspace/ancient-wisdom-mobile run dev` — run the Expo mobile app
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes to the development database only
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Flask (Python) with a small TypeScript RevenueCat connector bridge
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

Mobile session, device, and purchase-redemption tables are defined in `lib/db/src/schema/mobile.ts`. Apply development changes with `pnpm --filter @workspace/db run push`. Replit's managed PostgreSQL Publish flow syncs the development schema to production when the app is published; do not run DDL at application startup or in a deploy build command. The Flask mobile endpoint requires those tables and fails closed if they are missing. `artifacts/api-server/sql/mobile.sql` is a matching schema fixture for isolated API tests.

## Architecture decisions

- Web checkout remains Stripe; the mobile app uses RevenueCat and server-verified, single-use purchase redemption.
- Development Test Store products cannot authorize production analyses, even though their store identifier matches native products.

## Product

_Describe the high-level user-facing capabilities of this app once they exist._

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
