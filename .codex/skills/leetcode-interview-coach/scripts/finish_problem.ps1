param(
    [string[]]$Paths = @(),

    [string]$JavaPath,

    [string]$NotePath,

    [string]$ProblemTitle,

    [string]$Thinking,

    [string]$CommitMetadataJson,

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

function Get-FirstOutputLine {
    param(
        [object[]]$Output
    )

    $line = $Output | Select-Object -First 1
    if ($null -eq $line) {
        return ""
    }
    return ([string]$line).Trim()
}

function Read-Utf8JsonObject {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "JSON file does not exist: $Path"
    }

    $utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)
    $fullPath = (Resolve-Path -LiteralPath $Path).Path
    $text = [System.IO.File]::ReadAllText($fullPath, $utf8Strict)
    return $text | ConvertFrom-Json
}

function New-CommitMessageText {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,
        [Parameter(Mandatory = $true)]
        [string]$Summary,
        [Parameter(Mandatory = $true)]
        [string]$Timestamp
    )

    $thinkingLabel = -join @([char]0x601D, [char]0x8DEF, [char]0xFF1A)
    $submittedPrefix = "Codex " + [char]0x4E8E + " "
    $submittedSuffix = " " + (-join @([char]0x63D0, [char]0x4EA4))

    return (@(
        $Title,
        "",
        "$thinkingLabel$Summary",
        "",
        "$submittedPrefix$Timestamp$submittedSuffix"
    ) -join "`n") + "`n"
}

function Invoke-GitCommitWithUtf8Message {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $messagePath = Join-Path ([System.IO.Path]::GetTempPath()) ("leetcode-commit-message-{0}.txt" -f ([guid]::NewGuid().ToString("N")))
    [System.IO.File]::WriteAllText($messagePath, $Message, $utf8NoBom)
    try {
        & git commit -F $messagePath
    } finally {
        if (Test-Path -LiteralPath $messagePath) {
            Remove-Item -LiteralPath $messagePath -Force
        }
    }
}

if ($CommitMetadataJson) {
    $metadata = Read-Utf8JsonObject -Path $CommitMetadataJson
    if ($metadata.problemTitle) {
        $ProblemTitle = [string]$metadata.problemTitle
    }
    if ($metadata.thinking) {
        $Thinking = [string]$metadata.thinking
    }
}

if (-not $ProblemTitle) {
    throw "ProblemTitle is required. Pass -ProblemTitle or provide problemTitle in -CommitMetadataJson."
}
if (-not $Thinking) {
    throw "Thinking is required. Pass -Thinking or provide thinking in -CommitMetadataJson."
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
$message = New-CommitMessageText -Title $ProblemTitle -Summary $Thinking -Timestamp $timestamp
Invoke-GitCommitWithUtf8Message -Message $message

if ($NoPush) {
    return
}

$branch = Get-FirstOutputLine -Output (& git branch --show-current)
if (-not $branch) {
    throw "Cannot determine current Git branch."
}
$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$upstreamOutput = & git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null
$upstreamExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference
$upstream = Get-FirstOutputLine -Output $upstreamOutput
if ($upstreamExitCode -eq 0 -and $upstream) {
    & git push
} else {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $remoteOutput = & git config "branch.$branch.remote" 2>$null
    $ErrorActionPreference = $previousErrorActionPreference
    $remote = Get-FirstOutputLine -Output $remoteOutput
    if (-not $remote) {
        $remote = "origin"
    }
    & git push -u $remote HEAD
}
