<style>
  #pantalla_lista{display:none;}
  #pantalla_lista img{
    width:100%;
  }
  .cancion{
    display:flex;
  }
  .cancion .datostexto{flex:7;}
  .cancion>p{flex:1;}  
</style>
<div id="pantalla_lista">
  <img 
    src=""
    onerror="this.onerror=null; this.src='img/placeholder.png';"
    alt="Miniatura de la lista"
  >
  <h3>Titulo de la lista</h3>
  <div id="contienecanciones">
    
  </div>
</div>
<script>
  let contenedor_canciones = document.querySelector("#contienecanciones")
  
  fetch("api/lista.json")
  .then(function(respuesta){return respuesta.json()})
  .then(function(datos){
    datos.forEach(function(dato){
      let plantilla = document.querySelector("#plantilla_cancion")
      let clon = plantilla.content.cloneNode(true)
      clon.querySelector("h4").textContent = dato.song
      clon.querySelector("p").textContent = dato.album
      contenedor_canciones.appendChild(clon)
    })
  })
</script>
