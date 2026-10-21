$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
docker compose config --quiet
if ($LASTEXITCODE -ne 0) { throw 'Configuração Compose inválida.' }
docker compose up --build --wait
if ($LASTEXITCODE -ne 0) { throw 'Os serviços não ficaram saudáveis. Consulte docker compose logs.' }
python scripts/smoke.py
if ($LASTEXITCODE -ne 0) { throw 'Falha nos testes HTTP.' }
Write-Host 'Compose e testes HTTP concluídos. Acesse http://localhost:3000.'
