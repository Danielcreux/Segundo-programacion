<!-- Módulo listado de módulos -->

<style>
  <?php include "estilo.css";?>
</style>

<div id="listadodemodulos">
    <nav>
      <ul>
        <?php for($i = 0;$i<20;$i++){ ?>
        <li>Aplicación<?php echo $i; ?></li>
        <?php } ?>
      </ul>
    </nav>
    <section>
      <?php for($i = 0;$i<20;$i++){ ?>
      <article>
        <div class="logo">👀</div>
        <div class="texto">
          <h3>Título</h3>
          <p>Descripción del módulo</p>
          <button>Instalar</button>
        </div>
      </article>
      <?php } ?>
    </section>
    
</div>

<script>
  <?php include "comportamiento.js";?>
</script>

<!-- Módulo listado de módulos -->