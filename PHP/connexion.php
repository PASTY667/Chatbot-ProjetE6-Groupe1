<?php
require_once __DIR__ . '/connexion.inc.php';
require_once __DIR__ . '/header.inc.php';


$result = $conn->query("SELECT * FROM user");
$username

if(isset($_GET['username'])) {
  $result = $_GET['username'];
} else {
    echo "tg";
}

$conn->close();
?>

<form action="connexion.php" method="GET">
    <input type="text" name="username" placeholder="username">
    <input type="submit" name="button" id="">
</form>