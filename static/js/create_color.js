// Aplica cor ao textarea e mantém valor no input hidden (envia o value no form)
(function(){
  const colorInput = document.getElementById('text_color')
  const textarea = document.getElementById('content')
  const colorButton = document.getElementById('colorButton')
  const toggleBtn = document.getElementById('toggleSidebarBtn')
  const sidebar = document.querySelector('.sidebar')

  if (!colorInput || !textarea || !colorButton) return

  // Toggle sidebar quando clicado (se existir)
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function(e){
      e.preventDefault()
      sidebar.classList.toggle('open')
    })
  }

  // Aplica cor inicial
  textarea.style.color = colorInput.value
  colorButton.style.backgroundColor = colorInput.value

  // Abre o picker de cores ao clicar no botão
  colorButton.addEventListener('click', function(e){
    e.preventDefault()
    colorInput.click()
  })

  colorInput.addEventListener('input', function(e){
    textarea.style.color = e.target.value
    colorButton.style.backgroundColor = e.target.value
  })
})();
