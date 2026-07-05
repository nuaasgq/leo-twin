param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

$searchRoots = @("src", "examples", "tests", "frontend\src", "frontend\tests")
$patterns = @(
    "^\s*import\s+(stk|exata|glomosim|afsim|dds)\b",
    "^\s*from\s+(stk|exata|glomosim|afsim|dds)\b",
    "^\s*import\s+.*\s+from\s+['""](stk|exata|glomosim|afsim|dds)['""]"
)
$extensions = @("*.py", "*.ts", "*.tsx", "*.js", "*.jsx")

Push-Location $RepoRoot
try {
    $matches = @()
    foreach ($root in $searchRoots) {
        if (-not (Test-Path -LiteralPath $root)) {
            continue
        }
        foreach ($extension in $extensions) {
            $files = @(Get-ChildItem -Path $root -Recurse -File -Filter $extension -ErrorAction SilentlyContinue)
            foreach ($pattern in $patterns) {
                $matches += @($files | Select-String -Pattern $pattern -CaseSensitive:$false)
            }
        }
    }

    if ($matches.Count -gt 0) {
        foreach ($match in $matches) {
            Write-Host "$($match.Path):$($match.LineNumber): $($match.Line.Trim())"
        }
        throw "Forbidden external simulator/runtime import detected."
    }

    Write-Host "No forbidden external simulator/runtime imports detected."
}
finally {
    Pop-Location
}
