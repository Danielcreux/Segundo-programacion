<main>
  <?php
  $jsonFile = 'api/poemas.json'; // Ruta a tu archivo JSON
  $jsonData = file_get_contents($jsonFile);

  $data = json_decode($jsonData, true);

  foreach ($data['obras_poeticas'] as $libro) {
      echo "<h3>" . htmlspecialchars($libro['libro']) . "</h3>\n";
      
      if (isset($libro['año']) || isset($libro['estilo'])) {
          echo "<div class='libro-info'>";
          if (isset($libro['año'])) {
              echo "Año: " . htmlspecialchars($libro['año']) . " | ";
          }
          if (isset($libro['estilo'])) {
              echo "Estilo: " . htmlspecialchars($libro['estilo']);
          }
          echo "</div>\n";
      }
      
      if (isset($libro['poemas']) && is_array($libro['poemas'])) {
          echo "<ul>\n";
          foreach ($libro['poemas'] as $poema) {
              echo "  <li><a href='?p=poema&poema=" . htmlspecialchars($poema['titulo']) . "'>" . htmlspecialchars($poema['titulo']) . "</a></li>\n";
          }
          echo "</ul>\n";
      }
      echo "<br>\n";
  }
  ?>
</main>
