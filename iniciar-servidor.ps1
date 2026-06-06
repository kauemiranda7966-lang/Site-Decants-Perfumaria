$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$serverPath = Join-Path $root "server.py"
$requestedPort = if ($env:PORT) { [int]$env:PORT } else { 8000 }
$port = $requestedPort

try {
  $response = Invoke-WebRequest -Uri "http://localhost:$requestedPort/index.html" -UseBasicParsing -TimeoutSec 2
  if ($response.StatusCode -eq 200) {
    Write-Host "O servidor ja esta rodando em http://localhost:$requestedPort" -ForegroundColor Green
    exit 0
  }
} catch {
  # A porta esta livre ou esta ocupada por um processo sem resposta HTTP.
}

function Test-PortInUse([int]$portNumber) {
  $client = New-Object System.Net.Sockets.TcpClient
  try {
    $connection = $client.BeginConnect("127.0.0.1", $portNumber, $null, $null)
    return $connection.AsyncWaitHandle.WaitOne(300) -and $client.Connected
  } finally {
    $client.Close()
  }
}

if (Test-PortInUse $port) {
  $freePort = ($port + 1)..($port + 20) | Where-Object { -not (Test-PortInUse $_) } | Select-Object -First 1
  if (-not $freePort) {
    Write-Host "Nao encontrei uma porta livre entre $($port + 1) e $($port + 20)." -ForegroundColor Red
    exit 1
  }

  Write-Host "A porta $port esta ocupada por outro processo. Usando a porta $freePort." -ForegroundColor Yellow
  $port = $freePort
}

$candidates = @(
  @{ Path = (Join-Path $root ".venv\Scripts\python.exe"); Args = @() },
  @{ Path = (Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"); Args = @() }
)

$python = $candidates | Where-Object { Test-Path $_.Path } | Select-Object -First 1

if (-not $python) {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
  if ($pythonCommand) {
    $python = @{ Path = $pythonCommand.Source; Args = @() }
  }
}

if (-not $python) {
  $pyCommand = Get-Command py -ErrorAction SilentlyContinue
  if ($pyCommand) {
    $python = @{ Path = $pyCommand.Source; Args = @("-3") }
  }
}

if (-not $python) {
  Write-Host "Python nao foi encontrado nesta maquina." -ForegroundColor Red
  Write-Host "Instale o Python 3 e marque a opcao 'Add Python to PATH' durante a instalacao."
  exit 1
}

Write-Host "Iniciando Decant's Perfumaria em http://localhost:$port" -ForegroundColor Cyan
Set-Location $root
$env:PORT = $port
& $python.Path @($python.Args) $serverPath
