📁..
   ├─ 📁anterior
   │  ├─ 📁cabecera
   │  │  ├─ 📄comportamiento.js
   │  │  ├─ 📄estilo.css
   │  │  └─ 📄index.php
   │  ├─ 📁comun
   │  │  ├─ 📄estilo.css
   │  │  ├─ 📄Ubuntu-B.ttf
   │  │  └─ 📄Ubuntu-R.ttf
   │  ├─ 📁escritorio
   │  │  ├─ 📄comportamiento.js
   │  │  ├─ 📄estilo.css
   │  │  └─ 📄index.html
   │  ├─ 📁iniciarsesion
   │  │  ├─ 📄comportamiento.js
   │  │  ├─ 📄estilo.css
   │  │  └─ 📄index.html
   │  ├─ 📁listadodemodulos
   │  │  ├─ 📄comportamiento.js
   │  │  ├─ 📄estilo.css
   │  │  └─ 📄index.php
   │  ├─ 📁plantillas
   │  │  ├─ 📁calendario
   │  │  ├─ 📁fichas
   │  │  ├─ 📁formulario
   │  │  ├─ 📁grafica
   │  │  ├─ 📁Kanban
   │  │  │  ├─ 📄comportamiento.js
   │  │  │  ├─ 📄estilo.css
   │  │  │  ├─ 📄index.php
   │  │  │  └─ 📄kanban.json
   │  │  └─ 📁lista
   │  └─ 📄index.php
   ├─ 📁base de datos
   │  └─ 📄instalacion.sql
   ├─ 📁documentacion
   │  ├─ 📁__pycache__
   │  │  ├─ 📄arbol.cpython-313.pyc
   │  │  ├─ 📄cabeceras_stream.cpython-313.pyc
   │  │  └─ 📄docai.cpython-313.pyc
   │  ├─ 📄arbol.py
   │  ├─ 📄cabeceras.py
   │  ├─ 📄cabeceras_stream.py
   │  ├─ 📄docai.py
   │  ├─ 📄documentacion.py
   │  └─ 📄erp.md
   ├─ 📁documentacion2
   │  ├─ 📁__pycache__
   │  │  ├─ 📄arbol.cpython-313.pyc
   │  │  ├─ 📄cabeceras_stream.cpython-313.pyc
   │  │  └─ 📄docai.cpython-313.pyc
   │  ├─ 📄arbol.py
   │  ├─ 📄cabeceras.py
   │  ├─ 📄cabeceras_stream.py
   │  ├─ 📄docai.py
   │  ├─ 📄documentacion.py
   │  ├─ 📄erp_mejorado.md
   │  └─ 📄ollama_config.py
   ├─ 📁instalador
   │  └─ 📄index.php
   └─ 📁posterior
      ├─ 📄config.php
      ├─ 📄iniciarsesion.php
      └─ 📄listadodemodulos.php
# ..
## anterior

- [index.php](anterior\index.php)

    > ⚠️ Error llamando a Ollama: HTTP Error 500: Internal Server Error

    ```php
    <?php 
  session_start();
  if(!isset($_SESSION['usuario'])){
    header("Location: iniciarsesion/index.html");
    exit;
  }
?>
<!doctype html>
<html lang="es">
  <head>
    <title>ERP Joshue Daniel </title>
    <meta charset="utf-8">
    <link rel="stylesheet" href="comun/estilo.css">
  </head>
  <body>
    <?php include "cabecera/index.php" ?>
    <?php include "listadodemodulos/index.php" ?>
    
  </body>
</html> 
    ```
### cabecera

- [comportamiento.js](anterior\cabecera\comportamiento.js)
- [estilo.css](anterior\cabecera\estilo.css)

    > ⚠️ Error llamando a Ollama: HTTP Error 500: Internal Server Error

    ```css
    #superior{
  background:var(--solido-fondo);
  padding:20px;
  color:var(--solido-frente);
  font-weight:bold;
  display:flex;
  justify-content: space-between;
}
#inferior{
  background:white;
  padding:20px;
  color:black;
  font-weight:bold;
  display:flex;
  justify-content: space-between;
  border-bottom:1px solid var(--solido-fondo);
}
#inferior nav{
  display:flex;
}
    ```
- [index.php](anterior\cabecera\index.php)
