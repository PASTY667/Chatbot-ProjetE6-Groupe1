<?php
require_once __DIR__ . '/connexion.inc.php';
require_once __DIR__ . '/header.inc.php';

session_start();
if (!isset($_SESSION["errCode"]) || $_SESSION['errCode']!=0)
{
  header("location:connexion.php");
}


$result = $conn->query("SELECT * FROM user");

// Process the result set
if ($result->num_rows > 0) {
  // Output data of each row
  while($row = $result->fetch_assoc()) {
    echo "id: " . $row["id_user"] . "<br>";
  }
} else {
  echo "0 results";
}

$conn->close();
?>

<body>

</body>

<?php
require_once __DIR__ . '/footer.inc.php';
?>