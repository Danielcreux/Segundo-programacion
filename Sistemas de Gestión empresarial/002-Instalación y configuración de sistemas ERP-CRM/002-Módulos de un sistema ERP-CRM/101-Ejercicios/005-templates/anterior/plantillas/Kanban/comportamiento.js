let contenedor = document.querySelector("#kanban");
let dragged = null; // keep a reference to the dragged card

for (let columna = 1; columna <= 5; columna++) {
  let micolumna = document.createElement("div");
  micolumna.classList.add("columna");
  micolumna.textContent = "Col " + columna;
  contenedor.appendChild(micolumna);

  // allow drop
  micolumna.addEventListener("dragover", e => e.preventDefault());
  micolumna.addEventListener("dragenter", () => micolumna.classList.add("over"));
  micolumna.addEventListener("dragleave", () => micolumna.classList.remove("over"));

  micolumna.addEventListener("drop", e => {
    e.preventDefault();
    micolumna.classList.remove("over");
    if (dragged) micolumna.appendChild(dragged);
  });

  for (let i = 0; i < Math.round(Math.random() * 6); i++) {
    let tarjeta = document.createElement("div");
    tarjeta.classList.add("tarjeta");
    tarjeta.textContent = "T " + i;
    tarjeta.draggable = true;
    let color = document.createElement("input")
    color.setAttribute("type","color")
    color.value = "#FFA500"
    tarjeta.appendChild(color)
    color.onchange = function(){
      tarjeta.style.background = this.value
    }
    

    tarjeta.addEventListener("dragstart", e => {
      dragged = tarjeta;
      // optional: hint the type of action
      e.dataTransfer.effectAllowed = "move";
      console.log("La empiezas a mover");
    });

    tarjeta.addEventListener("dragend", () => {
      dragged = null;
    });

    micolumna.appendChild(tarjeta);
  }
}