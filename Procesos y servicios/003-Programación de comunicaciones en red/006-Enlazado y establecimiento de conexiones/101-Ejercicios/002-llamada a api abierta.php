<?php

$url = "https://covalently-untasked-daphne.ngrok-free.dev/api.php";

// La pregunta que quieres enviar
$question = "What is quantum computing?";

// Construimos los datos como application/x-www-form-urlencoded
$postData = http_build_query([
    "question" => $question
]);

$opts = [
    "http" => [
        "method"  => "POST",
        "header"  => "Content-Type: application/x-www-form-urlencoded\r\n" .
                     "Content-Length: " . strlen($postData) . "\r\n",
        "content" => $postData,
        "timeout" => 60
    ],
    "ssl" => [
        // Equivalente aproximado a curl -k (no recomendado en producción)
        "verify_peer"      => false,
        "verify_peer_name" => false,
    ]
];

$context  = stream_context_create($opts);
$response = @file_get_contents($url, false, $context);

if ($response === false) {
    $error = error_get_last();
    echo "Error calling remote API:\n";
    var_dump($error);
} else {
    echo $response . PHP_EOL;
}

