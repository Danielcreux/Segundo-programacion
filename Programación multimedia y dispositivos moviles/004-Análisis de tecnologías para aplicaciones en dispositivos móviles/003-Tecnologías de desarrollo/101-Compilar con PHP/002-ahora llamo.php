<?php
  ob_start();                  // Start capturing output
  include "001-prueba.php";    // Execute the PHP file
  $html = ob_get_clean();      // Get the generated HTML
  echo $html;                  // Show or process it
?>
