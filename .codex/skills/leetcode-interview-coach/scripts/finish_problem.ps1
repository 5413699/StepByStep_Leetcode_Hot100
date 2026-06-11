param(
    [string[]]$Paths = @(),

    [string]$JavaPath,

    [string]$NotePath,

    [Parameter(Mandatory = $true)]
    [string]$ProblemTitle,

    [Parameter(Mandatory = $true)]
    [string]$Thinking,

    [switch]$NoPush
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)

if (-not (Test-Path -LiteralPath ".git")) {
    throw "This script must run from the repository root."
}

function Add-NormalizedInputPath {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [System.Collections.Generic.List[string]]$Target,
        [string]$Path
    )

    if (-not $Path) {
        return
    }

    $candidate = $Path.Trim()
    if (-not $candidate) {
        return
    }

    if (-not (Test-Path -LiteralPath $candidate) -and $candidate.Contains(",")) {
        foreach ($part in ($candidate -split ",")) {
            Add-NormalizedInputPath -Target $Target -Path ($part.Trim().Trim("'").Trim('"'))
        }
        return
    }

    $Target.Add($candidate)
}

function Get-RepoRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $repoRoot = ((& git rev-parse --show-toplevel).Trim() -replace '\\', '/')
    $fullPath = ((Resolve-Path -LiteralPath $Path).Path -replace '\\', '/')
    if ($fullPath.StartsWith($repoRoot + "/", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $fullPath.Substring($repoRoot.Length + 1)
    }
    $normalized = $Path -replace '\\', '/'
    if ($normalized.StartsWith("./", [System.StringComparison]::Ordinal)) {
        return $normalized.Substring(2)
    }
    return $normalized
}

$resolvedPaths = New-Object System.Collections.Generic.List[string]
foreach ($path in $Paths) {
    Add-NormalizedInputPath -Target $resolvedPaths -Path $path
}
Add-NormalizedInputPath -Target $resolvedPaths -Path $JavaPath
Add-NormalizedInputPath -Target $resolvedPaths -Path $NotePath
$Paths = $resolvedPaths | Select-Object -Unique

if (-not $Paths -or $Paths.Count -eq 0) {
    throw "No paths were supplied. Use -JavaPath/-NotePath, or pass -Paths from the current PowerShell process."
}

foreach ($path in $Paths) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Path does not exist: $path"
    }
}

& mvn -q -DskipTests compile

$statusLines = & git -c core.quotePath=false status --porcelain=v1 --untracked-files=all
$trackedSet = New-Object System.Collections.Generic.HashSet[string]
foreach ($path in $Paths) {
    $normalized = Get-RepoRelativePath -Path $path
    [void]$trackedSet.Add($normalized)
}

$unrelated = New-Object System.Collections.Generic.List[string]
foreach ($line in $statusLines) {
    if ($line.Length -lt 4) {
        continue
    }
    $changedPath = $line.Substring(3) -replace '\\', '/'
    if (-not $trackedSet.Contains($changedPath)) {
        $unrelated.Add($line)
    }
}

if ($unrelated.Count -gt 0) {
    throw "Unrelated worktree changes exist. Commit refused:`n$($unrelated -join "`n")"
}

foreach ($path in $Paths) {
    & git add -- $path
}

$staged = & git diff --cached --name-only
if (-not $staged) {
    throw "No staged changes to commit."
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm zzz"
$message = @"
$ProblemTitle

思路：$Thinking

Codex 于 $timestamp 提交
"@

& git commit -m $message

if ($NoPush) {
    return
}

$branch = (& git branch --show-current).Trim()
$upstream = (& git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null)
if ($LASTEXITCODE -eq 0 -and $upstream) {
    & git push
} else {
    $remote = (& git config "branch.$branch.remote").Trim()
    if (-not $remote) {
        $remote = "origin"
    }
    & git push -u $remote HEAD
}
