# 使用 uv 初始化项目（Windows PowerShell）
# 在项目根目录执行: .\scripts\uv_install.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "正在安装 uv..."
    irm https://astral.sh/uv/install.ps1 | iex
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host "创建虚拟环境并安装依赖..."
uv sync

Write-Host "完成。运行应用: uv run python run.py"
Write-Host "运行测试: uv run pytest"
