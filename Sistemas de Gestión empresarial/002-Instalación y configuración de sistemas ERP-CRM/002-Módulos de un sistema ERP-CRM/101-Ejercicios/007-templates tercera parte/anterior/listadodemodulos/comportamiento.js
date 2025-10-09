/////////Aplicaciones///////////////////////////////////////////////
fetch("../posterior/listadodemodulos.php?ruta=aplicaciones")
.then(function(respuesta){
    return respuesta.json();
})
.then(function(datos){
    let contenedor = document.querySelector("section")
    datos.forEach(function(aplicacion){
     let articulo = `
              <article>
                <div class="logo">`+aplicacion.icono+`</div>
                <div class="texto">
                  <h3>`+aplicacion.nombre+`</h3>
                  <p>`+aplicacion.descripcion+`</p>
                  <button>Instalar</button>
                </div>
              </article>
          `;
        contenedor.innerHTML += articulo;
    })
})
/////////categorias_aplicaciones///////////////////////////////////////////////
fetch("../posterior/listadodemodulos.php?ruta=categorias")
.then(function(respuesta){
    return respuesta.json();
})
.then(function(datos){
    let contenedor = document.querySelector("ul")
    datos.forEach(function(aplicacion){
     let lista = `
              <li>`+aplicacion.nombre+`</li>
          `;
        contenedor.innerHTML += lista;
    })
      
})