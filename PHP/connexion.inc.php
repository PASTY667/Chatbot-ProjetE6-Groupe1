<?php
// Start the session
session_start();

// Local WAMP database configuration
$DATABASE_HOST = 'localhost';
$DATABASE_NAME = 'projet1_chatbot';
$DATABASE_USER = 'root';
$DATABASE_PASS = '';

// Create connection
$conn = new mysqli($DATABASE_HOST, $DATABASE_USER, $DATABASE_PASS, 'projet1_chatbot');
// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}