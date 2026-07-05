param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

$Assets = @(
    @{
        Path = "frontend\public\assets\nasa-satellite-kit\satellite-kit-body-2.glb"
        Sha256 = "175936434483f7b4d83d47fb36f8a2f900bea68b5ec231aa9ca84967432475b7"
    },
    @{
        Path = "frontend\public\assets\nasa-satellite-kit\satellite-kit-wings-2.glb"
        Sha256 = "b4b6d84ad0356a83dcbe640fda5a1c603c024e84591a65f650f662d3ef34bed1"
    },
    @{
        Path = "frontend\public\assets\nasa-satellite-kit\satellite-kit-radio-1.glb"
        Sha256 = "9b09e045fa455de38338748d66d12bee6a5d604427f33144cc39e8ff212b73d9"
    }
)

$Failures = New-Object System.Collections.Generic.List[string]

foreach ($asset in $Assets) {
    $path = Join-Path $RepoRoot $asset.Path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $Failures.Add("Missing asset: $($asset.Path)")
        continue
    }

    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $asset.Sha256) {
        $Failures.Add(
            "SHA-256 mismatch: $($asset.Path) expected $($asset.Sha256) actual $actual"
        )
    }
}

if ($Failures.Count -gt 0) {
    throw ($Failures -join [Environment]::NewLine)
}

Write-Host "Verified $($Assets.Count) frontend visual assets."
