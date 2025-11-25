<!doctype html>
<html lang="es">
  <head>
    <title>Poetica 2.0</title>
    <meta charset="utf-8">
    <link rel="stylesheet" href="estilo.css">
  </head>
  <body>
    <?php include "componentes/cabecera.php" ?>
    <?php
      if(!isset($_GET['p'])){
        include "componentes/home.php";
      }else{
        switch($_GET['p']){
          case "poemas":
            include "componentes/poemas.php";
            break;
          case "poema":
            include "componentes/poema.php";
            break;
          case "actores":
            include "componentes/actores.php";
            break;
          default:
            include "componentes/404.php";
        }
      }
    ?>  
    <?php include "componentes/piedepagina.php" ?>
  </body>
</html>