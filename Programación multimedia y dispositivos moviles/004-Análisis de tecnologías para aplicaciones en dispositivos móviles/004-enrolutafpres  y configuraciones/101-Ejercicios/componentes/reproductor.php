<style>
  #reproductor{
    width:91%;
    background:#541010;
    height:50px;
    border-radius:10px;
    padding:10px;
    position:fixed;
    top:80%;
    box-sizing:border-box;
    transition:all 1s;
    overflow:hidden;
  }
  .pantallacompleta{
    position:absolute !important;
    top:0px !important;
    left:0px;
    width:100% !important;
    height:100% !important;
  }
</style>
<section id="reproductor">
      <h3>Artista</h3>
      <img src="joshue.jpeg">
      <audio src="musica.mp3" controls>
    </section>
<script>
  let reproductor = document.querySelector("#reproductor");
  reproductor.onclick = function(){
    this.classList.add("pantallacompleta")
  }  
</script>
