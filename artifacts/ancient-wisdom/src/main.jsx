import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Localized home pages live at /ro/, /de/, ... so each language has its own
// indexable URL; ?lang= is still honoured for older links.
const PATH_LANGUAGES = ["ro", "de", "it", "fr", "es", "zh", "ar", "ja"];

function pageRequest() {
  const { pathname, search } = window.location;
  const query = new URLSearchParams(search);
  const segments = pathname.split("/").filter(Boolean);
  if (pathname === "/success") return { path: `/api/success${search}`, known: true };
  if (pathname === "/cancel") return { path: "/api/cancel", known: true };
  const isHome = segments.length === 0 || (segments.length === 1 && (segments[0] === "index.html" || PATH_LANGUAGES.includes(segments[0])));
  if (segments.length === 1 && PATH_LANGUAGES.includes(segments[0]) && !query.has("lang")) query.set("lang", segments[0]);
  return { path: `/api/page?${query}`, known: isHome };
}

function markNotFound() {
  const robots = document.querySelector('meta[name="robots"]') || document.head.appendChild(document.createElement("meta"));
  robots.setAttribute("name", "robots");
  robots.setAttribute("content", "noindex");
}

function Bootstrap() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const { path, known } = pageRequest();
    if (!known) markNotFound();
    fetch(path, { credentials: "include" })
      .then(response => response.json())
      .then(payload => payload && setData(known ? payload : { ...payload, page: "error", error: "This page does not exist. Start again from the home page." }))
      .catch(() => setData({ page: "error", error: "The application could not start." }));
  }, []);

  useEffect(() => {
    // The static guide section under the app only belongs on the home page.
    const seoHome = document.getElementById("seo-home");
    if (seoHome && data) seoHome.hidden = (data.page || "home") !== "home";
  }, [data]);

  return data ? <App {...data} /> : null;
}

createRoot(document.getElementById("root")).render(<Bootstrap />);
