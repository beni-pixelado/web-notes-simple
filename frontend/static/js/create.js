
function enviar() {
  const input = document.getElementById("upload")
  const file = input.files[0]

  if (!file) {
    alert("Choose an image first")
    return
  }

  const form = new FormData()
  form.append("imagem", file)

  fetch("/upload", {
    method: "POST",
    body: form
  })
}
