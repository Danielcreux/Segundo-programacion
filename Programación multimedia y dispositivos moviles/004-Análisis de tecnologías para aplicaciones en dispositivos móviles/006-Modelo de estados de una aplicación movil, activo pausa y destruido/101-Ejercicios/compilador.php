<?php

// ---- CONFIG ----
$destination = "C:\Users\Valentina\AndroidStudioProjects\Aplicacionweb2\app\src\main\assets";

// Ensure destination exists
if (!is_dir($destination)) {
    mkdir($destination, 0777, true);
}

// ---- 1. Compile index.php into index.html ----
ob_start();
include "index.php";
$html = ob_get_clean();

// Save compiled html
file_put_contents($destination . "index.html", $html);


// ---- 2. Recursive copy function ----
function copyRecursive($source, $dest) {
    if (is_dir($source)) {
        if (!is_dir($dest)) {
            mkdir($dest, 0777, true);
        }

        $items = scandir($source);
        foreach ($items as $item) {
            if ($item == "." || $item == "..") continue;

            $srcPath = $source . "/" . $item;
            $destPath = $dest . "/" . $item;

            if (is_dir($srcPath)) {
                copyRecursive($srcPath, $destPath);
            } else {
                copy($srcPath, $destPath);
            }
        }
    } else {
        copy($source, $dest);
    }
}


// ---- 3. Copy folders ----
$folders = ["static"];

foreach ($folders as $folder) {
    if (is_dir($folder)) {
        copyRecursive($folder, $destination . $folder);
    }
}

echo "✅ Compilation complete\n";

?>
