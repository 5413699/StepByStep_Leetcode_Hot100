param(
    [Parameter(Mandatory = $true)]
    [string[]]$Paths,

    [Parameter(Mandatory = $true)]
    [string]$ProblemTitle,

    [Parameter(Mandatory = $true)]
    [string]$Thinking,

    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath ".git")) {
    throw "This script must run from the repository root."
}

foreach ($path in $Paths) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Path does not exist: $path"
    }
}

& mvn -q -DskipTests compile

$statusLines = & git status --porcelain
$trackedSet = New-Object System.Collections.Generic.HashSet[string]
foreach ($path in $Paths) {
    $normalized = ($path -replace '\\', '/')
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
