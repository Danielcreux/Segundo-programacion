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
  var elementosmenu = ['Productos','Servicios','Empleados'];
  let menu = document.querySelector("#menu");
  elementosmenu.forEach(function(elemento){
    let boton = document.createElement("button");
    boton.textContent = elemento;
    menu.appendChild(boton);
  })
</script>
