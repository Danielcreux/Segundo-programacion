<?php include "funcionescss.php" ?>
:root {
  --colorprincipal:           <?= $baseHex ?>;
  --colorprincipal_claro:     <?= $baseLightHex ?>;
  --colorprincipal_claro2:    <?= $baseLighterHex ?>;
  --colorprincipal_oscuro:    <?= $baseDarkHex ?>;
  --colorprincipal_oscuro2:   <?= $baseDarkerHex ?>;

  --complementario:               <?= $compHex ?>;
  --complementario_suave:         <?= $compSoftHex ?>;
  --complementario_suave2:        <?= $compSofterHex ?>;
  --complementario_luminoso:      <?= $compBrightHex ?>;
  --complementario_oscuro:        <?= $compDarkHex ?>;
  --complementario_oscuro2:       <?= $compDarkerHex ?>;

  --hueco: 15px;
  
  --radio_empalme: 10px;
}

@import url('https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap');
body,html{
  padding:0px;
  margin:0px;
  width:100%;
  height:100%;
  font-family:ubuntu,sans-serif;
  background:var(--colorprincipal);
}
button{
  border:0px;
  border-radius:var(--radio_empalme);
  padding:5px;
  min-width:80px;
}