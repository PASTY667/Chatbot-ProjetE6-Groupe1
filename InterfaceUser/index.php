<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="./variables.css" />
    <link rel="stylesheet" href="css/style.css" />
    <link rel="stylesheet" href="css/sidebar.css" />
    <title>Franklin</title>
  </head>
  <header>
    <?php
        include 'sidebar.php';
    ?>
  </header>
  <body>
    <div class="newchatPage">
      <div class="newchatHeader">
        <img class="logo">
        <h1 class="newchatTitle">Franklin</h1>
      </div>
      <div class="newchatInput">
        <input type="button" class="addButton" value="+ PDF">
        <!-- <input class="addButton" type="file"> -->
        <input class="textInput" type="text">
        <input class="submitButton" type="submit" value=">">
      </div>
    </div>
  </body>
</html>
