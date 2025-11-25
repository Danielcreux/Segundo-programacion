<!doctype html>
<html lang="es">
  <head>
    <title></title>
    <meta charset="utf-8">
  </head>
  <body>
    <script>
      const parametros = new URLSearchParams(window.location.search);
      const nombre = parametros.get("nombre");
      console.log(nombre);
    </script>
  </body>
  
</html>
