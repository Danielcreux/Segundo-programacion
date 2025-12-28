<style>
  header button{
    background:magenta;
    color:white;
    padding:10px;
    border:none;
    border-radius:30px;
    min-width:40px;
   }
  #favoritas{
    display:grid;
    grid-template-columns:auto auto;
    gap:10px;
  }
  section article img{
    height:40px;
  }
  section article{
    gap:20px;
    display:flex;
    align-items:center;
    background:#292929;
    border-radius:10px;
  }
  section article p{
    font-weight:bold;
  }
  #pantalla_inicio{
  display:flex;
  flex-direction:column;
  gap:20px;
}
</style>

<div id="pantalla_inicio">
  <header>  
    <button>J</button>
    <button>Todos</button>
    <button>Música</button>
    <button>Podcasts</button>
  </header>
  <section id="favoritas">
    
   
  </section>
</div>

<script>
  let contenedor = document.querySelector("#favoritas")
  
  fetch("api/favoritos.json")
  .then(function(respuesta){return respuesta.json()})
  .then(function(datos){
    console.log(datos)
    datos.favorites.forEach(function(dato){
      let plantilla = document.querySelector("#elemento_lista")
      let instancia = plantilla.content.cloneNode(true)
      let articulo = instancia.querySelector("article")
      articulo.querySelector("p").textContent = dato.artist
      articulo.querySelector("img").setAttribute("src",dato.image)
      contenedor.appendChild(instancia)
      articulo.onclick = function(){
        console.log("Has hecho click en un articulo");
        document.querySelector("#pantalla_inicio").style.display = "none"
        document.querySelector("#pantalla_lista").style.display = "block"
      }
    })
  })
</script>
