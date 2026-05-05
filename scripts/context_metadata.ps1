# 1) Token
$tokenBody = @{ api_key = "sIln9RHtIfZJAdLt8djB7q5XPJ6kqXeu9cD3MuXXjwHri2yf"; subject = "debug-user" } | ConvertTo-Json -Compress
$tokenResp = Invoke-RestMethod -Uri "http://192.168.150.200:8000/auth/token" -Method POST -ContentType "application/json" -Body $tokenBody
$token = $tokenResp.access_token

# 2) Query non-stream
$body = @{
  query = "Quelles sont les routes API ?"
  collection_name = "documents_official"
  k = 5
} | ConvertTo-Json -Compress

Invoke-RestMethod -Uri "http://192.168.150.200:8000/chat/query" `
  -Method POST `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 12