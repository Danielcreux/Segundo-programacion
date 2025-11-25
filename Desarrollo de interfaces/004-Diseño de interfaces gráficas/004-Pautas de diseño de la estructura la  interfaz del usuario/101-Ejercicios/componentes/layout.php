<style>
  #principal{
    display:flex;width:100%;height:100%;
  }
  #principal nav{
    flex:1;background:var(--colorprincipal);padding:var(--hueco);
  }
  #principal section{
    flex:7;
    background:var(--colorprincipal_claro2);
    padding:var(--hueco);
    border-radius:calc(var(--radio_empalme)/2) 0px 0px 0px;
  }
</style>

<main id="principal">
  <nav>
    <?php include "menu.php"?>
  </nav>
  <section>
    <?php include "tabla.php"?>
  </section>
</main>

<script>
</script>
