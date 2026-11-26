import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./theme/tokens.css";
import "./styles.css";
import "./premium.css";
import "./celestial-ui.css";
import "./recovery.css";
import "./preview/preview.css";
import "./integration.css";
import "./theme/accent-geometry.css";
import "./theme/components.css";

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
