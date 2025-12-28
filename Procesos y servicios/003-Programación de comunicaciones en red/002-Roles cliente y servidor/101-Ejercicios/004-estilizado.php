<?php
// leer_imap.php

require 'imap_config.php';

if (!isset($IMAP_CONFIG) || !is_array($IMAP_CONFIG)) {
    die('Error: configuración IMAP no cargada.');
}

$mailbox = $IMAP_CONFIG['mailbox'];
$user    = $IMAP_CONFIG['user'];
$pass    = $IMAP_CONFIG['pass'];

// Carpeta para guardar imágenes adjuntas
$attachmentsDir = __DIR__ . '/attachments';
if (!is_dir($attachmentsDir)) {
    mkdir($attachmentsDir, 0775, true);
}

// ----------------- Helpers -----------------

/**
 * Decodifica cabeceras MIME (ej. Subject)
 */
function decode_mime_str($string, $targetCharset = 'UTF-8') {
    $elements = imap_mime_header_decode($string);
    $result = '';
    foreach ($elements as $element) {
        $charset = ($element->charset == 'default') ? 'ISO-8859-1' : $element->charset;
        $result .= iconv($charset, $targetCharset . '//TRANSLIT', $element->text);
    }
    return $result;
}

/**
 * Decodifica el cuerpo según la codificación indicada
 */
function decode_body($body, $encoding) {
    switch ($encoding) {
        case ENCBASE64:
            return base64_decode($body);
        case ENCQUOTEDPRINTABLE:
            return quoted_printable_decode($body);
        default:
            return $body;
    }
}

/**
 * Obtiene el cuerpo del mensaje en HTML si existe, o texto plano si no.
 * Devuelve HTML seguro para mostrar en la web.
 */
function get_body_as_html($inbox, $msgno) {
    $structure = imap_fetchstructure($inbox, $msgno);

    // Función recursiva para recorrer las partes
    $html = null;
    $plain = null;

    $walkParts = function ($structure, $prefix = '') use ($inbox, $msgno, &$html, &$plain, &$walkParts) {
        $partNumber = $prefix === '' ? '1' : $prefix;

        if (!isset($structure->parts)) {
            // Parte simple
            if ($structure->type == TYPETEXT) {
                $subtype = strtoupper($structure->subtype ?? '');
                $body = imap_fetchbody($inbox, $msgno, $partNumber);
                $body = decode_body($body, $structure->encoding);

                if ($subtype === 'HTML') {
                    $html = $body;
                } elseif ($subtype === 'PLAIN') {
                    // Guardamos solo si aún no hay texto plano
                    if ($plain === null) {
                        $plain = $body;
                    }
                }
            }
        } else {
            // Multipart
            foreach ($structure->parts as $index => $part) {
                $subPrefix = $prefix === '' ? strval($index + 1) : $prefix . '.' . ($index + 1);
                $walkParts($part, $subPrefix);
            }
        }
    };

    $walkParts($structure);

    if ($html !== null) {
        // Devolvemos directamente el HTML del correo (opcionalmente podrías sanearlo)
        return $html;
    } elseif ($plain !== null) {
        // Convertimos texto plano a HTML básico
        return nl2br(htmlspecialchars($plain, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'));
    } else {
        return '<p><em>(Sin contenido)</em></p>';
    }
}

/**
 * Guarda la primera imagen adjunta (attachment o inline) y devuelve la ruta relativa para usar en <img>.
 * Si no hay imagen, devuelve null.
 */
function get_first_image_attachment($inbox, $msgno, $attachmentsDir) {
    $structure = imap_fetchstructure($inbox, $msgno);
    if (!isset($structure->parts)) {
        return null; // Sin partes = probablemente sin adjuntos
    }

    $firstImagePath = null;

    $saveImage = function ($part, $partNumber) use ($inbox, $msgno, $attachmentsDir, &$firstImagePath) {
        // Tipos: 0 = text, 1 = multipart, 2 = message, 3 = application, 4 = audio, 5 = image, 6 = video, 7 = other
        $isImageType = ($part->type == 5); // 5 = image
        $subtype = strtoupper($part->subtype ?? '');

        if (!$isImageType) {
            // Algunos servidores pueden poner las imágenes como application/octet-stream,
            // si quisieras ser más agresivo, podrías comprobar solo la extensión del nombre de archivo.
            return;
        }

        // Comprobar que es attachment o inline con nombre de archivo
        $filename = null;

        if (isset($part->dparameters)) {
            foreach ($part->dparameters as $dparam) {
                if (strtolower($dparam->attribute) == 'filename') {
                    $filename = $dparam->value;
                    break;
                }
            }
        }

        if ($filename === null && isset($part->parameters)) {
            foreach ($part->parameters as $param) {
                if (strtolower($param->attribute) == 'name') {
                    $filename = $param->value;
                    break;
                }
            }
        }

        if ($filename === null) {
            // Nombre por defecto si no viene en cabecera
            $filename = 'image_' . $msgno . '_' . str_replace('.', '_', $partNumber) . '.' . strtolower($subtype);
        }

        // Normalizar nombre
        $filename = preg_replace('/[^\w\.\-]/', '_', $filename);

        $body = imap_fetchbody($inbox, $msgno, $partNumber);
        $body = decode_body($body, $part->encoding);

        $fullPath = rtrim($attachmentsDir, '/') . '/' . $filename;
        file_put_contents($fullPath, $body);

        // Guardamos ruta relativa para usar en HTML
        $firstImagePath = 'attachments/' . $filename;
    };

    $walkParts = function ($structure, $prefix = '') use (&$walkParts, $saveImage, &$firstImagePath) {
        if ($firstImagePath !== null) {
            return; // ya tenemos una imagen
        }

        if (!isset($structure->parts)) {
            // Parte simple
            $partNumber = $prefix === '' ? '1' : $prefix;
            $saveImage($structure, $partNumber);
        } else {
            foreach ($structure->parts as $index => $part) {
                $partNumber = $prefix === '' ? strval($index + 1) : $prefix . '.' . ($index + 1);
                // Si la parte es multipart, seguimos bajando
                if (isset($part->parts)) {
                    $walkParts($part, $partNumber);
                } else {
                    $saveImage($part, $partNumber);
                }

                if ($firstImagePath !== null) {
                    break;
                }
            }
        }
    };

    $walkParts($structure);

    return $firstImagePath;
}

// ----------------- Lógica principal -----------------

$inbox = @imap_open($mailbox, $user, $pass);

if (!$inbox) {
    die('No se pudo conectar al servidor IMAP: ' . imap_last_error());
}

$emails = imap_search($inbox, 'ALL');

if ($emails === false) {
    echo "No hay correos o error en la búsqueda.\n";
    imap_close($inbox);
    exit;
}

// Orden más nuevo primero y limitar a 10
rsort($emails);
$emails = array_slice($emails, 0, 10);

// Salida HTML básica
echo "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n";
echo "<meta charset=\"UTF-8\">\n<title>Correos como artículos</title>\n";
echo "<style>
*{padding:0px;margin:0px;}
body { font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; line-height: 1.6; }
article { border-bottom: 1px solid #ddd; padding: 1.5rem 0; }
article img { max-width: 100%; height: auto; display: block; margin: 1rem 0; }
article h2 { margin-top: 0; }
.meta { color: #666; font-size: 0.9em; margin-bottom: 0.5rem; }
h1,h2{text-align:center;}
</style>\n";
echo "</head>\n<body>
  
  <h1>Jose Vicente Carratalá Sanchis</h1>
  <h2>Blog personal</h2>
\n";

foreach ($emails as $num) {
    // Cabeceras para sacar asunto (título)
    $header = imap_headerinfo($inbox, $num);

    $subject = isset($header->subject) ? decode_mime_str($header->subject) : '(Sin asunto)';
    $from    = isset($header->fromaddress) ? decode_mime_str($header->fromaddress) : '';
    $date    = isset($header->date) ? $header->date : '';

    $bodyHtml = get_body_as_html($inbox, $num);
    $imageSrc = get_first_image_attachment($inbox, $num, $attachmentsDir);

    echo "<article>\n";
    echo "  <h3>" . htmlspecialchars($subject, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . "</h3>\n";
    echo "  <div class=\"meta\">";
    
    if ($date) {
        echo htmlspecialchars($date, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
    echo "</div>\n";

    if ($imageSrc !== null) {
        echo "  <img src=\"" . htmlspecialchars($imageSrc, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . "\" alt=\"Imagen del correo\">\n";
    }

    echo "  <div class=\"content\">\n";
    echo $bodyHtml;
    echo "  </div>\n";
    echo "</article>\n\n";
}

echo "</body>\n</html>";

imap_close($inbox);

