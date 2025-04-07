# PowerShell Test Script for Terminal MCP Server

Write-Host "PowerShell Test Script for Terminal MCP Server" -ForegroundColor Green
Write-Host "----------------------------------------------" -ForegroundColor Green
Write-Host ""

Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Host "Current Time: $(Get-Date -Format 'HH:mm:ss')"
Write-Host "Current Date: $(Get-Date -Format 'yyyy-MM-dd')"
Write-Host ""

Write-Host "Current working directory:" -ForegroundColor Yellow
Write-Host $(Get-Location)
Write-Host ""

Write-Host "Files in current directory:" -ForegroundColor Yellow
Get-ChildItem | Format-Table Name, Length, LastWriteTime
Write-Host ""

Write-Host "Creating a temporary file..." -ForegroundColor Yellow
"Hello from PowerShell via Terminal MCP!" | Out-File -FilePath temp_powershell_file.txt
"Created at: $(Get-Date)" | Add-Content -Path temp_powershell_file.txt
Write-Host "File created!"
Write-Host ""

Write-Host "Contents of temp_powershell_file.txt:" -ForegroundColor Yellow
Get-Content -Path temp_powershell_file.txt
Write-Host ""

Write-Host "System Information:" -ForegroundColor Yellow
Get-ComputerInfo | Select-Object WindowsProductName, OsVersion, OsArchitecture | Format-List
Write-Host ""

Write-Host "Done!" -ForegroundColor Green
