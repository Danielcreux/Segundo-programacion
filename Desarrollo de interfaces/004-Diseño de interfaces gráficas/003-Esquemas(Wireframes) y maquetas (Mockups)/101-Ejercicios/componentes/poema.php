<main>
  <h3>Página de poema</h3>
    <h4>
    <?php
      echo $_GET['poema'];
    ?>
    </h4>
    <?php
      $jsonFile = 'api/poemas/'.$_GET['poema'].'.json';
      $jsonData = file_get_contents($jsonFile);
      $poema = json_decode($jsonData, true);

      $poemaData = $poema['poema'];

      echo "<h1>" . htmlspecialchars($poemaData['titulo']) . "</h1>";
      echo "<h2>de " . htmlspecialchars($poemaData['autor']) . "</h2>";
      echo "<p><strong>Libro:</strong> " . htmlspecialchars($poemaData['libro']) . " (" . htmlspecialchars($poemaData['año']) . ")</p>";

      foreach ($poemaData['estrofas'] as $estrofa) {
          echo "<div class='estrofa'>";
          foreach ($estrofa['versos'] as $verso) {
              echo "<p>" . htmlspecialchars($verso) . "</p>";
          }
          echo "</div><br>";
      }

      echo "<div class='metadatos'>";
      echo "<h3>Temas:</h3><p>" . implode(", ", $poemaData['temas']) . "</p>";
      echo "<h3>Símbolos:</h3><p>" . implode(", ", $poemaData['simbolos']) . "</p>";
      echo "</div>";
      ?>
</main>
