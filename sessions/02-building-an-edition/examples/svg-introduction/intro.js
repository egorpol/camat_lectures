(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  function updateCircle() {
    const colour = $("circle-colour").value;
    const x = Number($("circle-position").value);
    const radius = Number($("circle-radius").value);
    const source = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 100">\n  <circle cx="${x}" cy="50" r="${radius}" fill="${colour}"/>\n</svg>`;
    $("circle-code").textContent = source;
    $("circle-picture").innerHTML = source;
    $("circle-picture").firstElementChild.setAttribute("aria-label", `A ${colour} circle at x ${x}, radius ${radius}`);
    $("circle-picture").firstElementChild.setAttribute("role", "img");
    $("position-value").value = String(x);
    $("radius-value").value = String(radius);
  }
  ["circle-colour", "circle-position", "circle-radius"].forEach((id) => $(id).addEventListener("input", updateCircle));
  $("reset-circle").addEventListener("click", () => {
    $("circle-colour").value = "black";
    $("circle-position").value = "70";
    $("circle-radius").value = "22";
    updateCircle();
  });
  function updateZoom() {
    const zoom = Number($("zoom-level").value);
    for (const id of ["raster-note", "vector-note"]) {
      $(id).setAttribute("width", String(32 * zoom));
      $(id).setAttribute("height", String(32 * zoom));
    }
    $("raster-note").style.imageRendering = $("show-pixels").checked ? "pixelated" : "auto";
    $("zoom-value").value = `${zoom}×`;
  }
  ["zoom-level", "show-pixels"].forEach((id) => $(id).addEventListener("input", updateZoom));
  let selected = false;
  function updateScore() {
    const pitch = $("pitch-choice").value;
    const variant = window.SVG_INTRO_SCORES[pitch];
    const enriched = $("extra-attributes").checked;
    $("score-stage").innerHTML = enriched ? variant.enriched : variant.plain;
    const root = $("score-stage").firstElementChild;
    root.setAttribute("role", "group");
    root.setAttribute("aria-label", `Pickup with an upper-staff eighth rest and a lower-staff ${variant.name} eighth note`);
    const note = $("score-stage").querySelector('[id="d1e60"]');
    // Make the whole note group easy to select, including the whitespace
    // between its stem, flag and notehead. The rectangle remains invisible.
    const box = note.getBBox();
    const hit = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    for (const [key, value] of Object.entries({x:box.x-20,y:box.y-20,width:box.width+40,height:box.height+40})) hit.setAttribute(key,String(value));
    hit.style.setProperty("fill", "transparent", "important");
    hit.style.setProperty("stroke", "none", "important");
    hit.setAttribute("aria-hidden", "true");
    hit.setAttribute("pointer-events", "all");
    note.append(hit);
    note.classList.toggle("is-selected", selected);
    note.setAttribute("tabindex", "0");
    note.setAttribute("role", "button");
    note.setAttribute("aria-label", `Highlight ${variant.name} pickup note d1e60`);
    note.setAttribute("aria-pressed", String(selected));
    const toggle = () => { selected = !selected; updateScore(); };
    note.addEventListener("click", toggle);
    note.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault(); toggle();
        $("score-stage").querySelector('[id="d1e60"]').focus();
      }
    });
    $("highlight-note").setAttribute("aria-pressed", String(selected));
    $("mei-code").textContent = variant.mei_note;
    const attributes = enriched ? variant.extra_attributes : variant.attributes;
    const lines = Object.entries(attributes).map(([key, value]) => `  ${key}="${value}"`).join("\n");
    $("score-code").textContent = `<g\n${lines}>\n  <!-- Shapes drawing this note -->\n</g>`;
    $("score-status").textContent = `${selected ? "Highlighted" : "Drawing address"}: d1e60 · MEI says ${variant.name}, eighth note. Colour does not change these values.`;
    $("pitch-explanation").textContent = pitch === "c"
      ? "Highlighting changes the drawing's appearance. The MEI still records C3 and an eighth-note duration."
      : "Changing pname from c to f changes the encoded pitch to F3. Re-engraving moves the note; its address d1e60 stays the same. This is a teaching experiment.";
  }
  $("highlight-note").addEventListener("click", () => { selected = !selected; updateScore(); });
  ["pitch-choice", "extra-attributes"].forEach((id) => $(id).addEventListener("change", updateScore));
  $("reset-score").addEventListener("click", () => {
    selected = false;
    $("pitch-choice").value = "c";
    $("extra-attributes").checked = false;
    updateScore();
  });
  updateCircle(); updateZoom(); updateScore();
})();
