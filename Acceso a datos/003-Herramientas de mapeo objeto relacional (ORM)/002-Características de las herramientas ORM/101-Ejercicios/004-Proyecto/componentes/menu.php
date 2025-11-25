<style>
  #menu{
    display:flex;
    flex-direction:column;
    gap:var(--hueco);
  }
  #menu button{
    background:var(--colorprincipal_claro2);
    border:none;
  }
</style>

<div id="menu">

</div>

<script>
  fetch("api/menu")
  .then(function(response){return response.json()})
  .then(function(datos){
  console.log(datos)
    var elementosmenu = datos;
    let menu = document.querySelector("#menu");
    elementosmenu.forEach(function(elemento){
      let boton = document.createElement("button");
      boton.textContent = elemento;
      menu.appendChild(boton);
    })
  })
  
</script>