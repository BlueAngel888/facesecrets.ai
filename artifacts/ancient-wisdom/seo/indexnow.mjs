// Tell Bing, Yandex, Seznam, Naver and other IndexNow engines which URLs
// changed. Run after a deploy: pnpm --filter @workspace/ancient-wisdom run seo:indexnow
// (Google does not use IndexNow; it reads sitemap.xml via Search Console.)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SITE_URL } from "./site.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const keyFile = fs.readdirSync(path.join(root, "public")).find(f => /^[0-9a-f]{32}\.txt$/.test(f));
if (!keyFile) throw new Error("IndexNow key file (public/<32 hex>.txt) is missing");
const key = keyFile.replace(".txt", "");
const urls = JSON.parse(fs.readFileSync(path.join(root, "dist", "public", "seo-pages.json"), "utf8"));

const response = await fetch("https://api.indexnow.org/indexnow", {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=utf-8" },
  body: JSON.stringify({ host: new URL(SITE_URL).host, key, keyLocation: `${SITE_URL}/${keyFile}`, urlList: urls }),
});
console.log(`IndexNow: HTTP ${response.status} for ${urls.length} URLs`);
if (response.status >= 400) process.exitCode = 1;
