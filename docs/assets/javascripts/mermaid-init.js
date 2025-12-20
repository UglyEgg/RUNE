// Mermaid initialization for MkDocs Material.
// This keeps Mermaid diagrams working on GitHub Pages without requiring a MkDocs plugin.
// If you later switch to SVG-only diagrams, you can remove this file and the extra_javascript entries.
(function () {
  if (typeof mermaid === "undefined") return;
  mermaid.initialize({
    startOnLoad: true,
    securityLevel: "strict"
  });
})();
