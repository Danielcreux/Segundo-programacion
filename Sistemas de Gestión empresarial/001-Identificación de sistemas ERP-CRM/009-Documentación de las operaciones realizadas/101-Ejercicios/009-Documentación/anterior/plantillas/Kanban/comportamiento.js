
// Creamos un contenedor vacío
var json = localStorage.getItem("kanbanJSON");
console.log(json);
  // Obtenemos origen de datos y lo cargamos
  if(json == null){
  fetch("kanban.json")
  .then(function(respuesta){
    return respuesta.json();
  })
  .then(function(datos){
    console.log(datos);
    json = datos;
    // Y lanzamos el proceso de representar
    representaKanban(datos);
  });
}else{
  representaKanban(JSON.parse(json));
}

// Funcion de representar el kanban
function representaKanban(datos){
  /*
    Lee el contenido de un json proporcionado
    Puebla las columnas automaticamente
    Crea tarjetas dentro de cada columna de forma automática
  */
  let contenedor = document.querySelector("#kanban");           // Seleccionamos un contenedor
  let dragged = null; // keep a reference to the dragged card
  let columnas = datos.columnas;                                 // Cargamos array de columnas
  columnas.forEach(function(columna){                           // Parseamos columna a columna
    let micolumna = document.createElement("div");              // Creamos un div
    micolumna.classList.add("columna");                         // Le añadimos la clase columna
    micolumna.textContent = "Col " + columna.nombre;            // Pequeña cabecera
    micolumna.setAttribute("data-title", columna.nombre);
    contenedor.appendChild(micolumna);                          // Lo añadimos al contenedor

    // allow drop
    micolumna.addEventListener("dragover", e => e.preventDefault());
    micolumna.addEventListener("dragenter", () => micolumna.classList.add("over"));
    micolumna.addEventListener("dragleave", () => micolumna.classList.remove("over"));

    micolumna.addEventListener("drop", e => {                   
      e.preventDefault();
      micolumna.classList.remove("over");                       
      if (dragged) micolumna.appendChild(dragged);              
      console.log("vamos a revisar cambios");
      // --- REGENERAR JSON DESDE DOM ---
      json = reconstruyeDesdeDOM(contenedor);
      console.log("JSON actualizado:", json);
      // Si quieres persistir localmente:
      localStorage.setItem("kanbanJSON", JSON.stringify(json));
      // --- ENVIAR AL BACKEND (PHP) ---
      fetch("../../../posterior/savekanban.php", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          // puedes añadir metadatos si quieres
          source: "kanban-ui",
          timestamp: Date.now(),
          data: json            // <-- el JSON reconstruido
        })
      })
      .then(r => r.json())
      .then(res => {
        console.log("Persistencia en SQLite:", res);
      })
      .catch(err => {
        console.error("Error guardando en backend:", err);
      });
    });
    let tarjetas = columna.tarjetas;                             // Obtenemos las tarjetas de esa columna
    tarjetas.forEach(function(mitarjeta){                       // Para cada una de las tarjetas
      let tarjeta = document.createElement("div");              // Creamos un div
      tarjeta.classList.add("tarjeta");                         // Añadimos clase
      tarjeta.textContent = "T " + mitarjeta.texto;             // Le ponemos un texto
      tarjeta.style.background = mitarjeta.color;                // Le ponemos color
      console.log(mitarjeta.color);
      tarjeta.draggable = true;                                 // La hacemos arrastrables
      let color = document.createElement("input");               // Le ponemos input de color
      color.setAttribute("type","color");
      color.value = "#FFA500";
      tarjeta.appendChild(color);
      color.onchange = function(){
        tarjeta.style.background = this.value;
      };
      

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
    });
  });
}

// --- Helpers para reconstruir JSON desde el DOM ---
function rgbToHex(rgb){
  // rgb(255, 165, 0) -> #ffa500
  const m = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
  if(!m) return rgb; // ya es hex o formato desconocido
  const toHex = n => Number(n).toString(16).padStart(2, "0");
  return "#" + toHex(m[1]) + toHex(m[2]) + toHex(m[3]);
}

function reconstruyeDesdeDOM(contenedor){
  const resultado = { columnas: [] };
  const cols = contenedor.querySelectorAll(".columna");

  cols.forEach(col => {
    // El título se creó como "Col <nombre>"
    // Recuperamos el nombre quitando el prefijo "Col "
    let titulo = "";
    // ChildNodes puede incluir texto + tarjetas; el primer nodo de texto contiene "Col <nombre>"
    // Para robustez, tomamos el primer nodo de texto de la columna
    for(const n of col.childNodes){
      if(n.nodeType === Node.TEXT_NODE && n.nodeValue.trim()){
        titulo = n.nodeValue.trim().replace(/^Col\s+/,"");
        break;
      }
    }

    const colJSON = { nombre: titulo, tarjetas: [] };
    col.querySelectorAll(".tarjeta").forEach(card => {
      // El primer nodo de texto es "T <texto>"
      let texto = "";
      if(card.firstChild && card.firstChild.nodeType === Node.TEXT_NODE){
        texto = card.firstChild.nodeValue.trim().replace(/^T\s+/,"");
      }else{
        // fallback si cambia la estructura
        texto = card.textContent.trim().replace(/^T\s+/,"");
      }

      // Color: preferimos el <input type="color"> si existe; si no, computamos el background
      const inputColor = card.querySelector('input[type="color"]');
      let color = getComputedStyle(card).backgroundColor;
      if(color.startsWith("rgb(")) color = rgbToHex(color);

      colJSON.tarjetas.push({ texto, color });
    });

    resultado.columnas.push(colJSON);
  });

  return resultado;
}
