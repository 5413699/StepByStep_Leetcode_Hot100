param(
    [Parameter(Mandatory = $true)]
    [string]$CategoryIndex,

    [Parameter(Mandatory = $true)]
    [ValidateSet("E", "M", "H")]
    [string]$Difficulty,

    [Parameter(Mandatory = $true)]
    [int]$ProblemNumber,

    [Parameter(Mandatory = $true)]
    [string]$ChineseTitle,

    [string]$ProblemToken,

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Get-BranchNamesFromMetadata {
    $branches = New-Object System.Collections.Generic.List[object]

    if (Test-Path -LiteralPath ".git\config") {
        Get-Content -LiteralPath ".git\config" -Encoding UTF8 | ForEach-Object {
            if ($_ -match '^\[branch "(.+)"\]') {
                $branches.Add([pscustomobject]@{ Name = $Matches[1]; Source = "config"; Priority = 3 })
            }
        }
    }

    if (Test-Path -LiteralPath ".git\refs\heads") {
        $headsRoot = (Resolve-Path ".git\refs\heads").Path
        Get-ChildItem -LiteralPath $headsRoot -Recurse -File | ForEach-Object {
            $relative = $_.FullName.Substring($headsRoot.Length + 1)
            $branches.Add([pscustomobject]@{ Name = ($relative -replace '\\', '/'); Source = "refs"; Priority = 3 })
        }
    }

    if (Test-Path -LiteralPath ".git\logs\HEAD") {
        Get-Content -LiteralPath ".git\logs\HEAD" -Encoding UTF8 | ForEach-Object {
            if ($_ -match 'checkout: moving from .+ to (.+)$') {
                $branches.Add([pscustomobject]@{ Name = $Matches[1]; Source = "logs"; Priority = 1 })
            }
            if ($_ -match 'refs/heads/(.+?) to refs/heads/(.+)$') {
                $branches.Add([pscustomobject]@{ Name = $Matches[1]; Source = "logs"; Priority = 1 })
                $branches.Add([pscustomobject]@{ Name = $Matches[2]; Source = "logs"; Priority = 1 })
            }
        }
    }

    return $branches | Where-Object { $_.Name -and $_.Name -ne "HEAD" }
}

$cleanTitle = ($ChineseTitle -replace '\s+', '')
if (-not $ProblemToken) {
    $ProblemToken = ("{0}{1:000}" -f $Difficulty.ToUpperInvariant(), $ProblemNumber)
}

$branches = Get-BranchNamesFromMetadata
$existing = $branches |
    Where-Object { $_.Name -match "-$([regex]::Escape($ProblemToken))-$([regex]::Escape($cleanTitle))$" } |
    Sort-Object `
        @{ Expression = "Priority"; Descending = $true },
        @{ Expression = {
            if ($_.Name -match '^\d+-(\d+)-') { [int]$Matches[1] } else { -1 }
        }; Descending = $true } |
    Select-Object -First 1

if ($existing) {
    $branchName = $existing.Name
} else {
    $maxOrder = -1
    foreach ($branch in ($branches | Select-Object -ExpandProperty Name -Unique)) {
        if ($branch -match "^$([regex]::Escape($CategoryIndex))-(\d+)-") {
            $order = [int]$Matches[1]
            if ($order -gt $maxOrder) {
                $maxOrder = $order
            }
        }
    }

    if ($maxOrder -lt 0) {
        throw "Could not infer next order for category index '$CategoryIndex'."
    }

    $branchName = "$CategoryIndex-$($maxOrder + 1)-$ProblemToken-$cleanTitle"
}

Write-Output $branchName

if ($DryRun) {
    return
}

$status = & git status --short
$dirty = $status | Where-Object { $_.Trim().Length -gt 0 }
if ($dirty) {
    throw "Worktree has changes. Review them before switching branches:`n$($dirty -join "`n")"
}

$currentBranch = (& git branch --show-current).Trim()
if ($currentBranch -eq $branchName) {
    return
}

$localBranches = & git branch --format "%(refname:short)"
if ($localBranches -contains $branchName) {
    & git switch $branchName
} else {
    & git switch -c $branchName
}
