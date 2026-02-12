<?php
require_once __DIR__ . '/connexion.inc.php';
require_once __DIR__ . '/header.inc.php';


$result = $conn->query("SELECT username FROM user");

if(isset($_GET['username'])) {
  $result = $_GET['username'];
} else {
    echo "tg";
}

$conn->close();
?>

<form action="index.php" method="GET">
    <input type="text" name="username" placeholder="username"><br>
    <input type="submit" name="button" id="">
</form>