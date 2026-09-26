import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

const root = document.getElementById("root");
const data = JSON.parse(root.dataset.page || "{}");
createRoot(root).render(<App {...data} />);