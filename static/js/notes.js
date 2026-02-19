// Espera a página carregar
document.addEventListener("DOMContentLoaded", () => {
  const notes = document.querySelectorAll(".note"); // pega todas as notas
  const maxLines = 7;

  notes.forEach(nota => {
    const lineHeight = parseFloat(getComputedStyle(nota).lineHeight);
    nota.style.maxHeight = (lineHeight * maxLines) + "px";
    nota.style.overflow = "hidden";
  });
});
