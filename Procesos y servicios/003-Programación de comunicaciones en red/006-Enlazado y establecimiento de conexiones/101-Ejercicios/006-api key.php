<?php

// Remote API (ngrok endpoint pointing to api.php)
$url = "https://covalently-untasked-daphne.ngrok-free.dev/api.php";

// This must match an api_key in your `api_keys` table
$apiKey = "TEST_API_KEY_JOCARSA_123";  // adjust to your real key

// Question to send
$question = "What is quantum computing?";

// Build POST body
$postData = http_build_query([
    "question" => $question
]);

$headers =
    "Content-Type: application/x-www-form-urlencoded\r\n" .
    "Content-Length: " . strlen($postData) . "\r\n" .
    "X-API-Key: " . $apiKey . "\r\n";

$opts = [
    "http" => [
        "method"  => "POST",
        "header"  => $headers,
        "content" => $postData,
        "timeout" => 60
    ],
    "ssl" => [
        // Equivalent to curl -k (for ngrok/testing only)
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
    exit;
}

echo $response . PHP_EOL;

