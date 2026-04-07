param(
    [string]$ApiBase = "http://localhost:8000",
    [string]$AdminKey = "change-this-admin-key",
    [string]$Subject = "arthur",
    [string]$ChatId = "chat_arthur_001",
    [string]$Scope = "user", # user|official
    [int]$K = 5,
    [string]$Question = "quelles sont les mesures de sécurité envisagées dans le projet ?",
    [string]$FilePath = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($FilePath)) {
    throw "FilePath is required. Example: -FilePath 'C:\\Users\\...\\document.pdf'"
}

if (-not (Test-Path $FilePath)) {
    throw "Fichier introuvable: $FilePath"
}

if ($Scope -eq "user" -and [string]::IsNullOrWhiteSpace($ChatId)) {
    throw "ChatId est requis quand Scope=user"
}

try {
    Write-Host "=== 1) Health ===" -ForegroundColor Cyan
    $health = Invoke-RestMethod -Uri "$ApiBase/health" -Method GET
    $health | ConvertTo-Json -Depth 6

    Write-Host "=== 2) Token ===" -ForegroundColor Cyan
    $tokenBody = @{ api_key = $AdminKey; subject = $Subject } | ConvertTo-Json -Compress
    $tokenResp = Invoke-RestMethod -Uri "$ApiBase/auth/token" -Method POST -ContentType "application/json" -Body $tokenBody
    $token = $tokenResp.access_token
    if (-not $token) { throw "Token non reçu." }

    if ($Scope -eq "official") {
        $collection = "documents_official"
    } else {
        $collection = "documents_user_$ChatId"
    }

    Write-Host "=== 3) Upload + Ingest ===" -ForegroundColor Cyan
    Add-Type -AssemblyName System.Net.Http
    $client = [System.Net.Http.HttpClient]::new()
    $client.DefaultRequestHeaders.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $token)

    $multipart = [System.Net.Http.MultipartFormDataContent]::new()
    $multipart.Add([System.Net.Http.StringContent]::new($Scope), "scope")
    if ($ChatId) { $multipart.Add([System.Net.Http.StringContent]::new($ChatId), "chat_id") }
    $multipart.Add([System.Net.Http.StringContent]::new($collection), "collection_name")

    $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
    # IMPORTANT: unary comma avoids PowerShell array unrolling into millions of ctor args
    $fileContent = [System.Net.Http.ByteArrayContent]::new((, $fileBytes))
    $fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/pdf")
    $fileName = [System.IO.Path]::GetFileName($FilePath)
    $multipart.Add($fileContent, "file", $fileName)

    $uploadResp = $client.PostAsync("$ApiBase/ingest/upload", $multipart).GetAwaiter().GetResult()
    $uploadText = $uploadResp.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    if (-not $uploadResp.IsSuccessStatusCode) {
        throw "Upload/Ingest failed: HTTP $($uploadResp.StatusCode) - $uploadText"
    }
    $uploadObj = $uploadText | ConvertFrom-Json
    $uploadObj | ConvertTo-Json -Depth 8

    Write-Host "=== 4) Chat Query ===" -ForegroundColor Cyan
    $chatBody = @{ query = $Question; collection_name = $collection; k = $K } | ConvertTo-Json -Compress
    $chatResp = Invoke-RestMethod -Uri "$ApiBase/chat/query" -Method POST -Headers @{ Authorization = "Bearer $token" } -ContentType "application/json" -Body $chatBody
    $chatResp | ConvertTo-Json -Depth 10

    Write-Host "`n=== Réponse LLM ===" -ForegroundColor Green
    Write-Host $chatResp.answer
}
catch {
    Write-Host "`nERREUR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
finally {
    Read-Host "`nAppuie sur Entrée pour fermer"
}
