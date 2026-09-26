import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

function Bootstrap() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const path = window.location.pathname === "/success"
      ? `/api/success${window.location.search}`
      : window.location.pathname === "/cancel"
        ? "/api/cancel"
        : `/api/page${window.location.search}`;
    fetch(path, { credentials: "include" })
      .then(response => response.json())
      .then(payload => payload && setData(payload))
      .catch(() => setData({ page: "error", error: "The application could not start." }));
  }, []);

  return data ? <App {...data} /> : null;
}

createRoot(document.getElementById("root")).render(<Bootstrap />);