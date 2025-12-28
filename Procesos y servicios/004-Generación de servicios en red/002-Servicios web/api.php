<?php
// api.php
$username = 'jocarsa'; // Change this
$password = 'jocarsa'; // Change this

// Check for valid credentials
if (!isset($_SERVER['PHP_AUTH_USER']) ||
    !isset($_SERVER['PHP_AUTH_PW']) ||
    $_SERVER['PHP_AUTH_USER'] != $username ||
    $_SERVER['PHP_AUTH_PW'] != $password) {
    header('WWW-Authenticate: Basic realm="Restricted Area"');
    header('HTTP/1.0 401 Unauthorized');
    die('Authentication required.');
}

// Get the endpoint from the query string
$endpoint = isset($_GET['endpoint']) ? $_GET['endpoint'] : '';

// Base directory for CSV files
$csvDir = 'monitor_data';

// Function to read CSV and return as JSON
function readCsvAsJson($csvFile) {
    if (!file_exists($csvFile)) {
        return ['error' => 'No data available.'];
    }
    $data = [];
    $file = fopen($csvFile, 'r');
    $header = fgetcsv($file);
    while ($row = fgetcsv($file)) {
        $data[] = array_combine($header, $row);
    }
    fclose($file);
    return $data;
}

// Serve data based on endpoint
header('Content-Type: application/json');
switch ($endpoint) {
    case 'cpu':
        echo json_encode(readCsvAsJson("$csvDir/cpu_usage.csv"));
        break;
    case 'ram':
        echo json_encode(readCsvAsJson("$csvDir/ram_usage.csv"));
        break;
    case 'disk_usage':
        echo json_encode(readCsvAsJson("$csvDir/disk_usage.csv"));
        break;
    case 'disk_io':
        $disk = isset($_GET['disk']) ? $_GET['disk'] : 'sda';
        echo json_encode(readCsvAsJson("$csvDir/disk_io_$disk.csv"));
        break;
    case 'bandwidth':
        $iface = isset($_GET['iface']) ? $_GET['iface'] : 'eth0';
        echo json_encode(readCsvAsJson("$csvDir/bandwidth_$iface.csv"));
        break;
    case 'apache_request_rate':
        echo json_encode(readCsvAsJson("$csvDir/apache_request_rate.csv"));
        break;
    default:
        echo json_encode(['error' => 'Invalid endpoint. Use: cpu, ram, disk_usage, disk_io, bandwidth, apache_request_rate']);
}
?>

