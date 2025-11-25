<?php
// Enlaza este archivo como si fuera un CSS:
// <link rel="stylesheet" href="colores.php?color=008080">
header("Content-Type: text/css; charset=utf-8");

// Color por defecto (teal) si no se pasa nada o es inválido
$inputColor = isset($_GET['color']) ? $_GET['color'] : '#B0C4DE';

// ========================
// Helpers básicos
// ========================
function normalizeHexColor($hex) {
    $hex = trim($hex);
    if ($hex[0] != '#') {
        $hex = '#'.$hex;
    }
    // 3 dígitos → 6 dígitos
    if (strlen($hex) == 4) {
        $r = str_repeat($hex[1], 2);
        $g = str_repeat($hex[2], 2);
        $b = str_repeat($hex[3], 2);
        $hex = '#'.$r.$g.$b;
    }
    // Validar
    if (!preg_match('/^#[0-9A-Fa-f]{6}$/', $hex)) {
        return '#008080'; // teal por defecto
    }
    return strtoupper($hex);
}

function hexToRgb($hex) {
    $hex = ltrim($hex, '#');
    return [
        'r' => hexdec(substr($hex, 0, 2)),
        'g' => hexdec(substr($hex, 2, 2)),
        'b' => hexdec(substr($hex, 4, 2)),
    ];
}

function rgbToHex($r, $g, $b) {
    return sprintf("#%02X%02X%02X", $r, $g, $b);
}

// ========================
// RGB ↔ HSL
// ========================
function rgbToHsl($r, $g, $b) {
    $r /= 255;
    $g /= 255;
    $b /= 255;

    $max = max($r, $g, $b);
    $min = min($r, $g, $b);
    $h = $s = $l = ($max + $min) / 2;

    if ($max == $min) {
        $h = $s = 0; // gris
    } else {
        $d = $max - $min;
        $s = $l > 0.5 ? $d / (2 - $max - $min) : $d / ($max + $min);

        if ($max == $r) {
            $h = ($g - $b) / $d + ($g < $b ? 6 : 0);
        } elseif ($max == $g) {
            $h = ($b - $r) / $d + 2;
        } else {
            $h = ($r - $g) / $d + 4;
        }
        $h /= 6;
    }

    return [
        'h' => $h * 360,     // 0–360
        's' => $s * 100,     // 0–100
        'l' => $l * 100      // 0–100
    ];
}

function hslToRgb($h, $s, $l) {
    $h /= 360;
    $s /= 100;
    $l /= 100;

    $r = $g = $b = 0;

    if ($s == 0) {
        $r = $g = $b = $l; // gris
    } else {
        $q = $l < 0.5 ? $l * (1 + $s) : $l + $s - $l * $s;
        $p = 2 * $l - $q;

        $r = hueToRgb($p, $q, $h + 1/3);
        $g = hueToRgb($p, $q, $h);
        $b = hueToRgb($p, $q, $h - 1/3);
    }

    return [
        'r' => round($r * 255),
        'g' => round($g * 255),
        'b' => round($b * 255)
    ];
}

function hueToRgb($p, $q, $t) {
    if ($t < 0) $t += 1;
    if ($t > 1) $t -= 1;
    if ($t < 1/6) return $p + ($q - $p) * 6 * $t;
    if ($t < 1/2) return $q;
    if ($t < 2/3) return $p + ($q - $p) * (2/3 - $t) * 6;
    return $p;
}

// ========================
// Helpers HSL
// ========================
function clamp($value, $min, $max) {
    return max($min, min($max, $value));
}

function adjustLightness($hsl, $deltaL) {
    $hsl['l'] = clamp($hsl['l'] + $deltaL, 0, 100);
    return $hsl;
}

function adjustSaturation($hsl, $deltaS) {
    $hsl['s'] = clamp($hsl['s'] + $deltaS, 0, 100);
    return $hsl;
}

// ========================
// Cálculos de colores
// ========================
$baseHex = normalizeHexColor($inputColor);
$baseRgb = hexToRgb($baseHex);
$baseHsl = rgbToHsl($baseRgb['r'], $baseRgb['g'], $baseRgb['b']);

// Complementario: hue + 180º
$compHsl = $baseHsl;
$compHsl['h'] = fmod($compHsl['h'] + 180, 360);

// Matices principal
$baseLightHsl      = adjustLightness($baseHsl, +15); // claro
$baseLighterHsl    = adjustLightness($baseHsl, +30); // más claro
$baseDarkHsl       = adjustLightness($baseHsl, -15); // oscuro
$baseDarkerHsl     = adjustLightness($baseHsl, -30); // más oscuro

// Complementarios suaves/luminosos y más tonos
$compSoftHsl       = adjustLightness(adjustSaturation($compHsl, -15), +10);
$compSofterHsl     = adjustLightness(adjustSaturation($compHsl, -25), +20);
$compBrightHsl     = adjustLightness(adjustSaturation($compHsl, -25), +35);
$compDarkHsl       = adjustLightness($compHsl, -20);
$compDarkerHsl     = adjustLightness($compHsl, -35);

// Convertir todo a RGB
$compRgb           = hslToRgb($compHsl['h'],       $compHsl['s'],       $compHsl['l']);
$baseLightRgb      = hslToRgb($baseLightHsl['h'],  $baseLightHsl['s'],  $baseLightHsl['l']);
$baseLighterRgb    = hslToRgb($baseLighterHsl['h'],$baseLighterHsl['s'],$baseLighterHsl['l']);
$baseDarkRgb       = hslToRgb($baseDarkHsl['h'],   $baseDarkHsl['s'],   $baseDarkHsl['l']);
$baseDarkerRgb     = hslToRgb($baseDarkerHsl['h'], $baseDarkerHsl['s'], $baseDarkerHsl['l']);
$compSoftRgb       = hslToRgb($compSoftHsl['h'],   $compSoftHsl['s'],   $compSoftHsl['l']);
$compSofterRgb     = hslToRgb($compSofterHsl['h'], $compSofterHsl['s'], $compSofterHsl['l']);
$compBrightRgb     = hslToRgb($compBrightHsl['h'], $compBrightHsl['s'], $compBrightHsl['l']);
$compDarkRgb       = hslToRgb($compDarkHsl['h'],   $compDarkHsl['s'],   $compDarkHsl['l']);
$compDarkerRgb     = hslToRgb($compDarkerHsl['h'], $compDarkerHsl['s'], $compDarkerHsl['l']);

// Convertir todo a HEX
$compHex           = rgbToHex($compRgb['r'],       $compRgb['g'],       $compRgb['b']);
$baseLightHex      = rgbToHex($baseLightRgb['r'],  $baseLightRgb['g'],  $baseLightRgb['b']);
$baseLighterHex    = rgbToHex($baseLighterRgb['r'],$baseLighterRgb['g'],$baseLighterRgb['b']);
$baseDarkHex       = rgbToHex($baseDarkRgb['r'],   $baseDarkRgb['g'],   $baseDarkRgb['b']);
$baseDarkerHex     = rgbToHex($baseDarkerRgb['r'], $baseDarkerRgb['g'], $baseDarkerRgb['b']);
$compSoftHex       = rgbToHex($compSoftRgb['r'],   $compSoftRgb['g'],   $compSoftRgb['b']);
$compSofterHex     = rgbToHex($compSofterRgb['r'], $compSofterRgb['g'], $compSofterRgb['b']);
$compBrightHex     = rgbToHex($compBrightRgb['r'], $compBrightRgb['g'], $compBrightRgb['b']);
$compDarkHex       = rgbToHex($compDarkRgb['r'],   $compDarkRgb['g'],   $compDarkRgb['b']);
$compDarkerHex     = rgbToHex($compDarkerRgb['r'], $compDarkerRgb['g'], $compDarkerRgb['b']);

?>