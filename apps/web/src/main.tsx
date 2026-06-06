import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./app";
import { applyTheme, getInitialTheme } from "./lib/theme";
import "./index.css";

// Apply the persisted theme before first paint to avoid a flash.
applyTheme(getInitialTheme());

const root = document.getElementById("root");
if (!root) throw new Error("Root element #root not found");

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
