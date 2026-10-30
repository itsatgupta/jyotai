import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";
import "./premium.css";
import "./celestial-ui.css";
import "./recovery.css";
import "./preview/preview.css";
import "./integration.css";

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
