<?php

// Remote API (your ngrok endpoint pointing to api.php)
$url = "https://covalently-untasked-daphne.ngrok-free.dev/api.php";

// Credentials must match $VALID_USER / $VALID_PASS in api.php
$user = 'myuser';        // same as in api.php
$pass = 'mypassword2';    // same as in api.php

// Question to send (you can change this or read from argv)
$question = "What is quantum computing?";

// Build POST data as application/x-www-form-urlencoded
$postData = http_build_query([
    "question" => $question
]);

// Build Authorization header (Basic Auth)
$authHeader = 'Authorization: Basic ' . base64_encode($user . ':' . $pass);

$opts = [
    "http" => [
        "method"  => "POST",
        "header"  =>
            "Content-Type: application/x-www-form-urlencoded\r\n" .
            "Content-Length: " . strlen($postData) . "\r\n" .
            $authHeader . "\r\n",
        "content" => $postData,
        "timeout" => 60
    ],
    "ssl" => [
        // Equivalent of curl -k: disable peer verification (for ngrok / tests)
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

