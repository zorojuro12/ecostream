# scripts/generate-tree.ps1
# Generates a clean project structure snapshot ignoring heavy/temp directories

$OutputFile = 'project_structure.txt'
$ExcludePatterns = @(
    'target', 'node_modules', '.git', 'venv', '.venv', 'Include', 'Lib', 
    'Scripts', '__pycache__', '.pytest_cache', '.cursor', '.idea', 
    '.vscode', 'bin', 'obj', 'project_structure.txt', 'nul', '.m2'
)

Write-Host 'Generating clean project structure...' -ForegroundColor Cyan

# Professional Get-ChildItem approach for better filtering control
Get-ChildItem -Recurse | Where-Object {
    $path = $_.FullName
    $shouldExclude = $false
    foreach ($p in $ExcludePatterns) {
        if ($path -like "*\$p*") { 
            $shouldExclude = $true
            break 
        }
    }
    -not $shouldExclude
} | ForEach-Object { 
    $indent = ''
    $depth = ($_.FullName.Replace((Get-Location).Path, '').Split('\').Count - 2)
    if ($depth -gt 0) { 
        $indent = '  ' * $depth + '|-- ' 
    }
    $indent + $_.Name 
} | Out-File -FilePath $OutputFile -Encoding utf8

Write-Host 'Done! Clean tree generated in project_structure.txt' -ForegroundColor Green
