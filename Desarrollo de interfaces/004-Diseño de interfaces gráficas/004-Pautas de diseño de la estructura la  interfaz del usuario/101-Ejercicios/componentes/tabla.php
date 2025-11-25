<style>
  #tabla{
    width:100%;
    border-collapse:collapse;
  }
  #tabla thead tr{
    background:var(--colorprincipal);
    border-radius:40px;
  }
  #tabla thead tr th:first-child{
    border-radius:var(--radio_empalme) 0px 0px var(--radio_empalme);
  }
  #tabla thead tr th:last-child{
    border-radius:0px var(--radio_empalme) var(--radio_empalme) 0px;
  }
  #tabla td, #tabla th{
    padding:calc(var(--hueco)/2);
  }
  #tabla tr{
    border-bottom:1px solid var(--colorprincipal);
  }
</style>

<table id="tabla">
  <thead></thead>
  <tbody></tbody>
</table>

<script>
  // Ruta al JSON (ajusta si está en otra carpeta)
  const RUTA_DATOS = 'api/datos.json';

  fetch(RUTA_DATOS)
    .then(respuesta => {
      if (!respuesta.ok) {
        throw new Error('Error al cargar datos.json');
      }
      return respuesta.json();
    })
    .then(datos => {
      construirTabla(datos);
    })
    .catch(error => {
      console.error(error);
    });

  function construirTabla(datos) {
    const tabla = document.getElementById('tabla');
    const thead = tabla.querySelector('thead');
    const tbody = tabla.querySelector('tbody');

    if (!Array.isArray(datos) || datos.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6">No hay datos</td></tr>';
      return;
    }

    // Usamos las claves del primer objeto como columnas
    const columnas = Object.keys(datos[0]);

    // Construir cabecera
    const trHead = document.createElement('tr');
    columnas.forEach(col => {
      const th = document.createElement('th');
      th.textContent = col;  // si quieres etiquetas “bonitas” aquí puedes mapear
      trHead.appendChild(th);
    });
    thead.appendChild(trHead);

    // Construir cuerpo
    datos.forEach(fila => {
      const tr = document.createElement('tr');
      columnas.forEach(col => {
        const td = document.createElement('td');
        td.textContent = fila[col];
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }
</script>

