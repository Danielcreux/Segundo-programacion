
// Creamos un contenedor vacío
var json = {}

// Obtenemos origen de datos y lo cargamos
fetch("kanban.json")
.then(function(respuesta){
  return respuesta.json()
})
.then(function(datos){
  console.log(datos)
  json = datos
  // Y lanzamos el proceso de representar
  representaKanban(datos)
})

// Funcion de representar el kanban
function representaKanban(datos){
  /*
    Lee el contenido de un json proporcionado
    Puebla las columnas automaticamente
    Crea tarjetas dentro de cada columna de forma automática
  */
  let contenedor = document.querySelector("#kanban");           // Seleccionamos un contenedor
  let dragged = null; // keep a reference to the dragged card
  let columnas = datos.columnas                                 // Cargamos array de columnas
  columnas.forEach(function(columna){                           // Parseamos columna a columna
    let micolumna = document.createElement("div");              // Creamos un div
    micolumna.classList.add("columna");                         // Le añadimos la clase columna
    micolumna.textContent = "Col " + columna.nombre;            // Pequeña cabecera
    contenedor.appendChild(micolumna);                          // Lo añadimos al contenedor

    // allow drop
    micolumna.addEventListener("dragover", e => e.preventDefault());
    micolumna.addEventListener("dragenter", () => micolumna.classList.add("over"));
    micolumna.addEventListener("dragleave", () => micolumna.classList.remove("over"));

    micolumna.addEventListener("drop", e => {                   // Cuando soltemos en una columna
      e.preventDefault();
      micolumna.classList.remove("over");                       // Le quitamos la clase
      if (dragged) micolumna.appendChild(dragged);              // Lo movemos a esa columna
    });
    let tarjetas = columna.tarjetas                             // Obtenemos las tarjetas de esa columna
    tarjetas.forEach(function(mitarjeta){                       // Para cada una de las tarjetas
      let tarjeta = document.createElement("div");              // Creamos un div
      tarjeta.classList.add("tarjeta");                         // Añadimos clase
      tarjeta.textContent = "T " + mitarjeta.texto;             // Le ponemos un texto
      tarjeta.style.background = mitarjeta.color                // Le ponemos color
      tarjeta.draggable = true;                                 // La hacemos arrastrables
      let color = document.createElement("input")               // Le ponemos input de color
      color.setAttribute("type","color")
      color.value = "#FFA500"
      tarjeta.appendChild(color)
      color.onchange = function(){
        tarjeta.style.background = this.value
      }
      

      tarjeta.addEventListener("dragstart", e => {              // Cuando iniciamos el drop, 
        dragged = tarjeta;
        // optional: hint the type of action
        e.dataTransfer.effectAllowed = "move";                  // Activamos efecto de mover
        console.log("La empiezas a mover");
      });

      tarjeta.addEventListener("dragend", () => {               // Cuando finalizamos del drop
        dragged = null;                                         // drag es null
      });

      micolumna.appendChild(tarjeta);
    })
  })
}