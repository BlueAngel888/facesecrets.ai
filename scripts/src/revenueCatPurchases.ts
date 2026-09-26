import { ReplitConnectors } from "@replit/connectors-sdk";

type Purchase = {
  product_id?: string;
  status?: string;
  store_purchase_identifier?: string;
  revenuecat_product?: Product;
  [key: string]: unknown;
};

type Product = {
  id?: string;
  store_identifier?: string;
  type?: string;
  one_time?: { is_consumable?: boolean | null } | null;
  [key: string]: unknown;
};

type ResourceList<T> = {
  items?: T[];
  next_page?: string | null;
};

const [projectId, customerId, configuredProductId] = process.argv.slice(2);
const testStoreAppId = process.env.REVENUECAT_TEST_STORE_APP_ID?.trim();
const production = Boolean(process.env.REPLIT_DEPLOYMENT);

async function main() {
  if (!projectId || !customerId || !configuredProductId || !testStoreAppId) {
    throw new Error("RevenueCat purchase verification unavailable");
  }

  const connectors = new ReplitConnectors();
  const projectPath = `/v2/projects/${encodeURIComponent(projectId)}`;

  async function getPage<T>(path: string, customerFirstPage: boolean): Promise<ResourceList<T>> {
    const response = await connectors.proxy("revenuecat", path, { method: "GET" });
    // RevenueCat does not create the customer until the SDK first sees them.
    if (response.status === 404 && customerFirstPage) return { items: [], next_page: null };
    if (!response.ok) throw new Error("RevenueCat purchase verification unavailable");
    return (await response.json()) as ResourceList<T>;
  }

  async function listAll<T>(initialPath: string, customer = false): Promise<T[]> {
    let path: string | null = initialPath;
    const visited = new Set<string>();
    const items: T[] = [];
    while (path) {
      if (!path.startsWith(`${projectPath}/`) || visited.has(path) || visited.size >= 1000) {
        throw new Error("RevenueCat purchase verification unavailable");
      }
      visited.add(path);
      const page: ResourceList<T> = await getPage<T>(path, customer && visited.size === 1);
      if (!Array.isArray(page.items)) {
        throw new Error("RevenueCat purchase verification unavailable");
      }
      items.push(...page.items);
      path = page.next_page ?? null;
    }
    return items;
  }

  const [catalog, purchases] = await Promise.all([
    listAll<Product>(`${projectPath}/products?limit=100`),
    listAll<Purchase>(
      `${projectPath}/customers/${encodeURIComponent(customerId)}/purchases?limit=100`,
      true,
    ),
  ]);
  const products = catalog.filter(
    (product) => {
      const matchesConfiguredProduct =
        product.id === configuredProductId ||
        product.store_identifier === configuredProductId;
      const isAllowedApp = production
        ? typeof product.app_id === "string" && product.app_id !== testStoreAppId
        : product.app_id === testStoreAppId;
      return matchesConfiguredProduct && isAllowedApp;
    },
  );
  const productById = new Map(
    products
      .filter((product): product is Product & { id: string } => typeof product.id === "string")
      .map((product) => [product.id, product]),
  );
  const configuredPurchases = purchases.flatMap((purchase) => {
    const product = purchase.product_id ? productById.get(purchase.product_id) : undefined;
    return product ? [{ ...purchase, revenuecat_product: product }] : [];
  });

  // Stdout is a JSON purchase list only; never print diagnostics or credentials.
  process.stdout.write(JSON.stringify(configuredPurchases));
}

main().catch(() => {
  process.stderr.write("RevenueCat purchase verification unavailable\n");
  process.exitCode = 1;
});