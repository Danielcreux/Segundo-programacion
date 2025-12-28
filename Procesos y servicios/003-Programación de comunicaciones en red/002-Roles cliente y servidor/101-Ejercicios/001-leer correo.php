<?php
// leer_imap.php

// Ruta absoluta recomendada (fuera de /var/www/html si es posible)
require 'imap_config.php';

// Comprobar que $IMAP_CONFIG existe
if (!isset($IMAP_CONFIG) || !is_array($IMAP_CONFIG)) {
    die('Error: configuración IMAP no cargada.');
}

$mailbox = $IMAP_CONFIG['mailbox'];
$user    = $IMAP_CONFIG['user'];
$pass    = $IMAP_CONFIG['pass'];

// Abrir bandeja de entrada
$inbox = @imap_open($mailbox, $user, $pass);

if (!$inbox) {
    die('No se pudo conectar al servidor IMAP: ' . imap_last_error());
}

// Buscar todos los mensajes
$emails = imap_search($inbox, 'ALL');

if ($emails === false) {
    echo "No hay correos o error en la búsqueda.\n";
} else {
    // Mostrar los últimos 10
    rsort($emails); // del más nuevo al más antiguo
    $emails = array_slice($emails, 0, 10);

    foreach ($emails as $num) {
        $overview = imap_fetch_overview($inbox, $num, 0)[0];

        echo "----------------------------------------\n";
        echo "Nº:      {$overview->msgno}\n";
        echo "Fecha:   {$overview->date}\n";
        echo "De:      {$overview->from}\n";
        echo "Asunto:  {$overview->subject}\n";
        echo "Leído:   " . ($overview->seen ? 'Sí' : 'No') . "\n";
    }
}

imap_close($inbox);

