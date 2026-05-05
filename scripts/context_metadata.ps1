param(
    [string]$ApiBase  = "http://192.168.150.200:8000",
    [string]$AdminKey = "sIln9RHtIfZJAdLt8djB7q5XPJ6kqXeu9cD3MuXXjwHri2yf",
    [string]$OfficialPdf = "C:\Users\arthur.domy-bonnel\Downloads\AnnexeDocumentationAPI_ProjetChatbotGRP01_20260427.pdf",
    [string]$UserPdf = "C:\Users\arthur.domy-bonnel\Downloads\ProjetChabot_CompteRenduRevue2_DomyBonnelLouboutinDomingo.pdf",
    [string]$UserChatId = "chat_test_user_001"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Net.Http
$httpClient = [System.Net.Http.HttpClient]::new()
$httpClient.Timeout = [System.TimeSpan]::FromMinutes(5)

# --------------------------------------------------------------
# Helpers
# --------------------------------------------------------------
function Write-Section($title) {
    Write-Host "`n$("-" * 60)" -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host "$("-" * 60)" -ForegroundColor Cyan
}

function Write-Pass($msg) { Write-Host "  [PASS] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red }
function Write-Info($msg) { Write-Host "  [INFO] $msg" -ForegroundColor Gray }

$global:passed = 0
$global:failed = 0

function Assert-Eq($label, $got, $expected) {
    if ($got -eq $expected) {
        Write-Pass "$label => $got"
        $global:passed++
    } else {
        Write-Fail "$label => got '$got', expected '$expected'"
        $global:failed++
    }
}

function Assert-NotNull($label, $value) {
    if ($null -ne $value -and $value -ne "") {
        Write-Pass "$label est non-nul"
        $global:passed++
    } else {
        Write-Fail "$label est nul ou vide"
        $global:failed++
    }
}

function Assert-HttpError($label, $statusCode, $expectedCode) {
    if ($statusCode -eq $expectedCode) {
        Write-Pass "$label => HTTP $statusCode (attendu $expectedCode)"
        $global:passed++
    } else {
        Write-Fail "$label => HTTP $statusCode (attendu $expectedCode)"
        $global:failed++
    }
}

# --------------------------------------------------------------
# Fonctions API
# --------------------------------------------------------------

function Get-Token($subject, $key = $AdminKey) {
    $body = @{ api_key = $key; subject = $subject } | ConvertTo-Json -Compress
    $resp = Invoke-RestMethod -Uri "$ApiBase/auth/token" -Method POST -ContentType "application/json" -Body $body
    return $resp.access_token
}

function Invoke-ChatStream($token, $payload) {
    $json = $payload | ConvertTo-Json -Compress
    $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, "$ApiBase/chat/query/stream")
    $request.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $token)
    $request.Content = [System.Net.Http.StringContent]::new($json, [System.Text.Encoding]::UTF8, "application/json")

    $response = $httpClient.SendAsync($request, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()

    if (-not $response.IsSuccessStatusCode) {
        return @{ StatusCode = [int]$response.StatusCode; Body = "" }
    }

    $stream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
    $reader = [System.IO.StreamReader]::new($stream)
    $fullText = ""

    Write-Host "    [STREAMING] : " -ForegroundColor Yellow -NoNewline
    while (-not $reader.EndOfStream) {
        $buffer = [char[]]::new(128)
        $readCount = $reader.Read($buffer, 0, $buffer.Length)
        if ($readCount -gt 0) {
            $chunk = [string]::new($buffer, 0, $readCount)
            Write-Host $chunk -NoNewline
            $fullText += $chunk
        }
    }
    Write-Host "" # Retour à la ligne

    $reader.Close()
    return @{ StatusCode = [int]$response.StatusCode; Body = $fullText }
}

function Invoke-Upload($token, $filePath, $scope, $chatId, $collection) {
    $multipart = [System.Net.Http.MultipartFormDataContent]::new()
    $multipart.Add([System.Net.Http.StringContent]::new($scope), "scope")
    if ($chatId) { $multipart.Add([System.Net.Http.StringContent]::new($chatId), "chat_id") }
    if ($collection) { $multipart.Add([System.Net.Http.StringContent]::new($collection), "collection_name") }
    $fs = [System.IO.File]::OpenRead($filePath)
    $fc = [System.Net.Http.StreamContent]::new($fs)
    $fc.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/pdf")
    $multipart.Add($fc, "file", [System.IO.Path]::GetFileName($filePath))

    $req = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, "$ApiBase/ingest/upload")
    $req.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $token)
    $req.Content = $multipart
    $resp = $httpClient.SendAsync($req).GetAwaiter().GetResult()
    $text = $resp.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    $fs.Dispose()
    return @{ StatusCode = [int]$resp.StatusCode; Body = $text }
}

# --------------------------------------------------------------
# TEST 0 - Health
# --------------------------------------------------------------
Write-Section "TEST 0 - Health check"
$health = Invoke-RestMethod -Uri "$ApiBase/health" -Method GET
Assert-Eq "status" $health.status "ok"
Assert-Eq "chroma_ok" $health.chroma_ok $true

# --------------------------------------------------------------
# TEST 1 - Authentification
# --------------------------------------------------------------
Write-Section "TEST 1 - Authentification"
$adminToken = Get-Token "test-admin"
Assert-NotNull "Token admin" $adminToken

try {
    Get-Token "hacker" "wrong-key"
    Write-Fail "Mauvaise cle aurait du retourner 401"
} catch {
    Assert-HttpError "Mauvaise cle API" $_.Exception.Response.StatusCode.value__ 401
}

# --------------------------------------------------------------
# TEST 2 - User sans doc
# --------------------------------------------------------------
Write-Section "TEST 2 - User sans doc (Stream)"
$userToken = Get-Token "user-no-doc"
# ATTENTION: Votre backend /stream exige actuellement collection_name
$payload = @{
    query = "Quelles sont les routes API ?";
    collection_name = "documents_official"; # Ajouté car nécessaire pour votre endpoint stream actuel
    k = 2
}
$r = Invoke-ChatStream $userToken $payload
Assert-Eq "HTTP 200 (official seulement)" $r.StatusCode 200

# --------------------------------------------------------------
# TEST 3 - User avec doc (Fusion)
# --------------------------------------------------------------
Write-Section "TEST 3 - User avec doc fusion (Stream)"
if ([string]::IsNullOrWhiteSpace($UserPdf) -or -not (Test-Path $UserPdf)) {
    Write-Info "UserPdf non fourni - TEST 3 ignore"
} else {
    $userToken2 = Get-Token "user-with-doc"
    $up = Invoke-Upload $userToken2 $UserPdf "user" $UserChatId $null
    Assert-Eq "Upload HTTP 200" $up.StatusCode 200

    # Note: Votre backend stream actuel n'utilise pas encore la fusion automatique (resolve_target_collections)
    # Dans le TEST 3 du .ps1
    $payload = @{
        query = "Explique le projet en utilisant les infos de l'école et de mon document.";
        include_user_collection = $true;
        chat_id = $UserChatId; # Sera transformé en documents_user_chat_test_user_001
        use_official = $true;   # Pour forcer la fusion avec l'officiel
        k = 3
    }
    $r4 = Invoke-ChatStream $userToken2 $payload
    Assert-Eq "HTTP 200 (fusion/user)" $r4.StatusCode 200

    if ($r4.Body -notlike "*aucun passage pertinent*") {
        Write-Pass "Contenu present dans la réponse"
        $global:passed++
    } else {
        Write-Fail "Aucun contexte trouve dans le stream"
        $global:failed++
    }
}

# --------------------------------------------------------------
# TEST 4 - Override collection_name
# --------------------------------------------------------------
Write-Section "TEST 4 - Override collection_name (Stream)"
$payload = @{
    query = "Qu'est-ce qu'un JWT selon le glossaire ?";
    collection_name = "documents_official";
    k = 2
}
$r5 = Invoke-ChatStream $adminToken $payload
Assert-Eq "HTTP 200 override" $r5.StatusCode 200

# --------------------------------------------------------------
# TEST 5 - Cas limites
# --------------------------------------------------------------
Write-Section "TEST 5 - Cas limites"
try {
    # On teste l'erreur 422 (validation FastAPI) sur le stream
    $badPayload = @{ query = ""; k = 1 } | ConvertTo-Json -Compress
    $req = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, "$ApiBase/chat/query/stream")
    $req.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $adminToken)
    $req.Content = [System.Net.Http.StringContent]::new($badPayload, [System.Text.Encoding]::UTF8, "application/json")
    $resp = $httpClient.SendAsync($req).GetAwaiter().GetResult()
    Assert-HttpError "Query vide" [int]$resp.StatusCode 422
} catch {
    Write-Info "Erreur lors du test 5: $($_.Exception.Message)"
}

# --------------------------------------------------------------
# TEST 6 - Ingestion Officielle
# --------------------------------------------------------------
Write-Section "TEST 6 - Ingestion document officiel"
if ([string]::IsNullOrWhiteSpace($OfficialPdf) -or -not (Test-Path $OfficialPdf)) {
    Write-Info "OfficialPdf non fourni - TEST 6 ignore"
} else {
    $up2 = Invoke-Upload $adminToken $OfficialPdf "official" $null "documents_official"
    Assert-Eq "Upload officiel HTTP 200" $up2.StatusCode 200
}

# --------------------------------------------------------------
# BILAN
# --------------------------------------------------------------
Write-Host "`n$("-" * 60)" -ForegroundColor White
$finalColor = if ($global:failed -eq 0) { "Green" } else { "Red" }
Write-Host "  BILAN : $($global:passed) PASS  |  $global:failed FAIL" -ForegroundColor $finalColor
Write-Host "$("-" * 60)`n" -ForegroundColor White

if ($global:failed -gt 0) { exit 1 } else { exit 0 }