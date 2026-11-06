import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Placeholder } from "./Placeholder";
import { TITLE } from "./about";

const root = document.getElementById("root");
if (!root) throw new Error("index.html has no #root to render into.");

document.title = TITLE;
createRoot(root).render(
  <StrictMode>
    <Placeholder />
  </StrictMode>,
);
