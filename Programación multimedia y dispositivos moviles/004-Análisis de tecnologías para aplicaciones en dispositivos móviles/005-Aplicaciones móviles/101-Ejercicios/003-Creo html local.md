app/
 └─ src/
     └─ main/
         ├─ java/
         ├─ res/
         └─ assets/
              └─ index.html
              
<!doctype html>
<html>
    <head>
        <style>
            h1{color:red;}
        </style>
    </head>
    <body>
        <h1>Hola mundo</h1>
        <script>
            let titulo = document.querySelector("h1")
            titulo.onclick = function(){
                titulo.style.color = "green";
            }
        </script>
    </body>
</html>