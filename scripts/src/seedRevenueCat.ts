import { ReplitConnectors } from "@replit/connectors-sdk";

// Run with pnpm --filter @workspace/scripts exec tsx src/seedRevenueCat.ts.
// Idempotently provisions the Ancient Wisdom consumable report catalog.
const connectors = new ReplitConnectors();
const base = "/v2";
const productIdentifier = "ancient_wisdom_report";

async function api<T>(path: string, method = "GET", body?: object): Promise<T> {
  const response = await connectors.proxy("revenuecat", `${base}${path}`, {
    method,
    ...(body ? { headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {}),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(`${method} ${path} (${response.status}): ${JSON.stringify(payload)}`);
  return payload as T;
}

type Item = { id: string; name?: string; type?: string; app_id?: string; store_identifier?: string; lookup_key?: string; is_current?: boolean };
type List = { items: Item[] };

async function ensure<T extends Item>(path: string, items: Item[], predicate: (item: Item) => boolean, body: object): Promise<T> {
  const existing = items.find(predicate);
  return (existing ?? await api<T>(path, "POST", body)) as T;
}

async function main() {
  const projects = await api<List>("/projects");
  const project = await ensure<Item>("/projects", projects.items, p => p.name === "Ancient Wisdom", { name: "Ancient Wisdom" });
  const scope = `/projects/${project.id}`;
  const apps = (await api<List>(`${scope}/apps`)).items;
  let test = apps.find(a => a.type === "test_store");
  if (!test) {
    // New projects normally contain a Test Store app. If not, create one.
    test = await api<Item>(`${scope}/apps`, "POST", { name: "Ancient Wisdom Test Store", type: "test_store" });
  }
  const ios = await ensure<Item>(`${scope}/apps`, apps, a => a.type === "app_store", {
    name: "Ancient Wisdom iOS", type: "app_store", app_store: { bundle_id: "com.ancientwisdom.portrait" },
  });
  const android = await ensure<Item>(`${scope}/apps`, apps, a => a.type === "play_store", {
    name: "Ancient Wisdom Android", type: "play_store", play_store: { package_name: "com.ancientwisdom.portrait" },
  });
  const products = (await api<List>(`${scope}/products`)).items;
  const ensureProduct = (app: Item) => ensure<Item>(`${scope}/products`, products, p => p.app_id === app.id && p.store_identifier === productIdentifier, {
    app_id: app.id, store_identifier: productIdentifier, type: "consumable",
    display_name: "One portrait report",
    ...(app.id === test.id ? { title: "One portrait report" } : {}),
  });
  const [testProduct, iosProduct, androidProduct] = await Promise.all([ensureProduct(test), ensureProduct(ios), ensureProduct(android)]);
  const prices = await api<{ currency: string }[]>(`${scope}/products/${testProduct.id}/test_store_prices`);
  if (!prices.some(p => p.currency === "EUR")) {
    await api(`${scope}/products/${testProduct.id}/test_store_prices`, "POST", {
      prices: [{ amount_micros: 29990000, currency: "EUR" }, { amount_micros: 29990000, currency: "USD" }],
    });
  }
  const entitlements = (await api<List>(`${scope}/entitlements`)).items;
  const entitlement = await ensure<Item>(`${scope}/entitlements`, entitlements, e => e.lookup_key === "portrait_report", {
    lookup_key: "portrait_report", display_name: "Portrait Report",
  });
  await api(`${scope}/entitlements/${entitlement.id}/actions/attach_products`, "POST", {
    product_ids: [testProduct.id, iosProduct.id, androidProduct.id],
  });
  const offerings = (await api<List>(`${scope}/offerings`)).items;
  const offering = await ensure<Item>(`${scope}/offerings`, offerings, o => o.lookup_key === "default", {
    lookup_key: "default", display_name: "Portrait Report",
  });
  if (!offering.is_current) await api(`${scope}/offerings/${offering.id}`, "PATCH", { is_current: true });
  const packages = (await api<List>(`${scope}/offerings/${offering.id}/packages`)).items;
  const pkg = await ensure<Item>(`${scope}/offerings/${offering.id}/packages`, packages, p => p.lookup_key === "$rc_custom_report", {
    lookup_key: "$rc_custom_report", display_name: "One report",
  });
  await api(`${scope}/packages/${pkg.id}/actions/attach_products`, "POST", {
    products: [testProduct, iosProduct, androidProduct].map(product => ({ product_id: product.id, eligibility_criteria: "all" })),
  });
  console.log(JSON.stringify({ projectId: project.id, testAppId: test.id, iosAppId: ios.id, androidAppId: android.id, productIdentifier }));
}

main().catch(error => { console.error(error); process.exitCode = 1; });