param(
    [string]$ApiBase = "http://localhost:8000",
    [string]$AdminKey = "change-this-admin-key",
    [string]$Subject = "arthur",
    [string]$ChatId = "chat_arthur_001",
    [string]$Scope = "user", # user|official
    [int]$K = 5,
    [string]$Question = "quelles sont les mesures de sécurité envisagées dans le projet ?",
    [string]$FilePath = "",
    [switch]$StreamResponse
)

$ErrorActionPreference = "Stop"
$fileStream = $null

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

    $fileStream = [System.IO.File]::OpenRead($FilePath)
    $fileContent = [System.Net.Http.StreamContent]::new($fileStream)
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

    if ($StreamResponse.IsPresent) {
        Write-Host "=== Streaming response ===" -ForegroundColor Yellow
        $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, "$ApiBase/chat/query/stream")
        $request.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $token)
        $request.Content = [System.Net.Http.StringContent]::new($chatBody, [System.Text.Encoding]::UTF8, "application/json")

        $streamResp = $client.SendAsync($request, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
        if (-not $streamResp.IsSuccessStatusCode) {
            $streamErr = $streamResp.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            throw "Stream chat failed: HTTP $($streamResp.StatusCode) - $streamErr"
        }

        $responseStream = $streamResp.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
        $reader = [System.IO.StreamReader]::new($responseStream)
        while (-not $reader.EndOfStream) {
            $charCode = $reader.Read()
            if ($charCode -ge 0) {
                Write-Host -NoNewline ([char]$charCode)
            }
        }
        Write-Host ""
    }
    else {
        $chatResp = Invoke-RestMethod -Uri "$ApiBase/chat/query" -Method POST -Headers @{ Authorization = "Bearer $token" } -ContentType "application/json" -Body $chatBody
        $chatResp | ConvertTo-Json -Depth 10

        Write-Host "`n=== Réponse LLM ===" -ForegroundColor Green
        Write-Host $chatResp.answer
    }
}
catch {
    Write-Host "`nERREUR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
finally {
    if ($fileStream) { $fileStream.Dispose() }
    Read-Host "`nAppuie sur Entrée pour fermer"
}
