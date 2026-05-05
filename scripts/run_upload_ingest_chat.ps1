param(
    [string]$ApiBase = "http://localhost:8000",
    [string]$AdminKey = "change-this-admin-key",
    [string]$Subject = "arthur",
    [string]$ChatId = "chat_arthur_001",
    [string]$Scope = "user", # user|official
    [int]$K = 5,
    [string]$Question = "quelles sont les mesures de sécurité envisagées dans le projet ?",
    [string]$FilePath = "",
    [string]$UserFilePath = "",
    [string]$AdminQuestion = "Quels points clés figurent dans la documentation officielle ?",
    [string]$UserQuestion = "Quels éléments figurent dans le document utilisateur importé ?",
    [string]$UserChatId = "chat_user_demo_001",
    [switch]$DualCollectionDemo,
    [switch]$StreamResponse
)

$ErrorActionPreference = "Stop"
$fileStream = $null

if ($DualCollectionDemo.IsPresent) {
    if ([string]::IsNullOrWhiteSpace($FilePath)) {
        throw "FilePath is required for admin/official document in dual demo mode."
    }
    if ([string]::IsNullOrWhiteSpace($UserFilePath)) {
        throw "UserFilePath is required for user document in dual demo mode."
    }
    if (-not (Test-Path $FilePath)) {
        throw "Fichier admin introuvable: $FilePath"
    }
    if (-not (Test-Path $UserFilePath)) {
        throw "Fichier utilisateur introuvable: $UserFilePath"
    }
}
else {
    if ([string]::IsNullOrWhiteSpace($FilePath)) {
        throw "FilePath is required. Example: -FilePath 'C:\\Users\\...\\document.pdf'"
    }

    if (-not (Test-Path $FilePath)) {
        throw "Fichier introuvable: $FilePath"
    }

    if ($Scope -eq "user" -and [string]::IsNullOrWhiteSpace($ChatId)) {
        throw "ChatId est requis quand Scope=user"
    }
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

    Add-Type -AssemblyName System.Net.Http
    $client = [System.Net.Http.HttpClient]::new()
    $client.DefaultRequestHeaders.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $token)

    function Invoke-UploadIngest {
        param(
            [Parameter(Mandatory = $true)][string]$UploadScope,
            [Parameter(Mandatory = $false)][string]$UploadChatId,
            [Parameter(Mandatory = $true)][string]$UploadCollection,
            [Parameter(Mandatory = $true)][string]$UploadFilePath
        )

        $localFileStream = $null
        try {
            $multipart = [System.Net.Http.MultipartFormDataContent]::new()
            $multipart.Add([System.Net.Http.StringContent]::new($UploadScope), "scope")
            if ($UploadChatId) { $multipart.Add([System.Net.Http.StringContent]::new($UploadChatId), "chat_id") }
            $multipart.Add([System.Net.Http.StringContent]::new($UploadCollection), "collection_name")

            $localFileStream = [System.IO.File]::OpenRead($UploadFilePath)
            $fileContent = [System.Net.Http.StreamContent]::new($localFileStream)
            $fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/pdf")
            $fileName = [System.IO.Path]::GetFileName($UploadFilePath)
            $multipart.Add($fileContent, "file", $fileName)

            $uploadResp = $client.PostAsync("$ApiBase/ingest/upload", $multipart).GetAwaiter().GetResult()
            $uploadText = $uploadResp.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            if (-not $uploadResp.IsSuccessStatusCode) {
                throw "Upload/Ingest failed for scope=${UploadScope}, collection=${UploadCollection}: HTTP $($uploadResp.StatusCode) - $uploadText"
            }
            return ($uploadText | ConvertFrom-Json)
        }
        finally {
            if ($localFileStream) { $localFileStream.Dispose() }
        }
    }

    function Invoke-StreamChat {
        param(
            [Parameter(Mandatory = $true)][string]$StreamQuestion,
            [Parameter(Mandatory = $true)][string]$StreamCollection
        )
        $chatBody = @{ query = $StreamQuestion; collection_name = $StreamCollection; k = $K } | ConvertTo-Json -Compress
        $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, "$ApiBase/chat/query/stream")
        $request.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $token)
        $request.Content = [System.Net.Http.StringContent]::new($chatBody, [System.Text.Encoding]::UTF8, "application/json")

        $streamResp = $client.SendAsync($request, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
        if (-not $streamResp.IsSuccessStatusCode) {
            $streamErr = $streamResp.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            throw "Stream chat failed for collection=${StreamCollection}: HTTP $($streamResp.StatusCode) - $streamErr"
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

    if ($DualCollectionDemo.IsPresent) {
        $adminCollection = "documents_official"
        $userCollection = "documents_user_$UserChatId"

        Write-Host "=== 3) Upload + Ingest (ADMIN/OFFICIAL) ===" -ForegroundColor Cyan
        $adminIngest = Invoke-UploadIngest -UploadScope "official" -UploadCollection $adminCollection -UploadFilePath $FilePath
        $adminIngest | ConvertTo-Json -Depth 8

        Write-Host "=== 4) Upload + Ingest (USER) ===" -ForegroundColor Cyan
        $userIngest = Invoke-UploadIngest -UploadScope "user" -UploadChatId $UserChatId -UploadCollection $userCollection -UploadFilePath $UserFilePath
        $userIngest | ConvertTo-Json -Depth 8

        Write-Host "=== 5) Stream question on ADMIN collection ===" -ForegroundColor Yellow
        Invoke-StreamChat -StreamQuestion $AdminQuestion -StreamCollection $adminCollection

        Write-Host "=== 6) Stream question on USER collection ===" -ForegroundColor Yellow
        Invoke-StreamChat -StreamQuestion $UserQuestion -StreamCollection $userCollection
    }
    else {
        if ($Scope -eq "official") {
            $collection = "documents_official"
        } else {
            $collection = "documents_user_$ChatId"
        }

        Write-Host "=== 3) Upload + Ingest ===" -ForegroundColor Cyan
        $uploadObj = Invoke-UploadIngest -UploadScope $Scope -UploadChatId $ChatId -UploadCollection $collection -UploadFilePath $FilePath
        $uploadObj | ConvertTo-Json -Depth 8

        Write-Host "=== 4) Chat Query ===" -ForegroundColor Cyan
        $chatBody = @{ query = $Question; collection_name = $collection; k = $K } | ConvertTo-Json -Compress

        if ($StreamResponse.IsPresent) {
            Write-Host "=== Streaming response ===" -ForegroundColor Yellow
            Invoke-StreamChat -StreamQuestion $Question -StreamCollection $collection
        }
        else {
            $chatResp = Invoke-RestMethod -Uri "$ApiBase/chat/query" -Method POST -Headers @{ Authorization = "Bearer $token" } -ContentType "application/json" -Body $chatBody
            $chatResp | ConvertTo-Json -Depth 10

            Write-Host "`n=== Réponse LLM ===" -ForegroundColor Green
            Write-Host $chatResp.answer
        }
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
