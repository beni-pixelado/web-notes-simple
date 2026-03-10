// Wait for the page to load
document.addEventListener("DOMContentLoaded", () => {
  const notes = document.querySelectorAll(".note"); // get all notes
  const maxLines = 7;

  notes.forEach(nota => {
    const lineHeight = parseFloat(getComputedStyle(nota).lineHeight);
    nota.style.maxHeight = (lineHeight * maxLines) + "px";
    nota.style.overflow = "hidden";
  });
});
