// Apply color to textarea and keep value in hidden input (sends the value in the form)
(function(){
  const colorInput = document.getElementById('text_color')
  const textarea = document.getElementById('content')
  const colorButton = document.getElementById('colorButton')
  const toggleBtn = document.getElementById('toggleSidebarBtn')
  const sidebar = document.querySelector('.sidebar')

  if (!colorInput || !textarea || !colorButton) return

  // Toggle sidebar when clicked (if exists)
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function(e){
      e.preventDefault()
      sidebar.classList.toggle('open')
    })
  }

  // Apply initial color
  textarea.style.color = colorInput.value
  colorButton.style.backgroundColor = colorInput.value

  // Open color picker when button is clicked
  colorButton.addEventListener('click', function(e){
    e.preventDefault()
    colorInput.click()
  })

  colorInput.addEventListener('input', function(e){
    textarea.style.color = e.target.value
    colorButton.style.backgroundColor = e.target.value
  })
})();
