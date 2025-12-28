<?php
// api_bandwidth_usage.php
$username = 'your_username'; // Change this
$password = 'your_password'; // Change this

// Check for valid credentials
if (!isset($_SERVER['PHP_AUTH_USER']) ||
    !isset($_SERVER['PHP_AUTH_PW']) ||
    $_SERVER['PHP_AUTH_USER'] != $username ||
    $_SERVER['PHP_AUTH_PW'] != $password) {
    header('WWW-Authenticate: Basic realm="Restricted Area"');
    header('HTTP/1.0 401 Unauthorized');
    die('Authentication required.');
}

// CSV file path
$csvFile = 'bandwidth_usage_history.csv';

// Check if file exists
if (!file_exists($csvFile)) {
    header('Content-Type: application/json');
    die(json_encode(['error' => 'No data available.']));
}

// Read CSV and convert to JSON
$data = [];
$file = fopen($csvFile, 'r');
$header = fgetcsv($file);
while ($row = fgetcsv($file)) {
    $data[] = [
        'date' => $row[0],
        'interface' => $row[1],
        'bytes_sent' => (int)$row[2],
        'bytes_recv' => (int)$row[3],
        'packets_sent' => (int)$row[4],
        'packets_recv' => (int)$row[5]
    ];
}
fclose($file);

// Output as JSON
header('Content-Type: application/json');
echo json_encode($data);
?>

