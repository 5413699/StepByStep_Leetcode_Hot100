param(
    [Parameter(Mandatory = $true)]
    [string]$JavaPath,

    [Parameter(Mandatory = $true)]
    [string]$NotePath,

    [Parameter(Mandatory = $true)]
    [string]$ProblemTitle,

    [Parameter(Mandatory = $true)]
    [string]$Thinking,

    [string]$SolutionContent,
    [string]$NoteContent,
    [string]$StatementMarkdown,
    [string]$ProcessMarkdown,
    [string]$ComplexityMarkdown,
    [string[]]$Pitfalls = @(),
    [string]$TagPlanJson,
    [string]$ReadinessJson,
    [string]$ConversationDigestJson,
    [string]$SyncInputJson,
    [string]$WorkflowConfigPath,
    [switch]$SkipSiyuan,
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8 = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"

if (-not (Test-Path -LiteralPath ".git")) {
    throw "This script must run from the repository root."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Update-MarkedMarkdownRegion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    $start = "<!-- codex-leetcode-start -->"
    $end = "<!-- codex-leetcode-end -->"
    $existing = ""
    if (Test-Path -LiteralPath $Path) {
        $existing = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    }

    $region = "$start`n`n$($Content.Trim())`n`n$end"
    if ($existing.Contains($start) -and $existing.Contains($end)) {
        $before = $existing.Substring(0, $existing.IndexOf($start)).TrimEnd()
        $afterStart = $existing.IndexOf($end) + $end.Length
        $after = $existing.Substring($afterStart).TrimStart()
        $updated = "$before`n`n$region`n`n$after".Trim() + "`n"
    } elseif ($existing.Trim().Length -gt 0) {
        $updated = $existing.TrimEnd() + "`n`n" + $region + "`n"
    } else {
        $updated = $region + "`n"
    }
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $fullPath = (Resolve-Path -LiteralPath $Path).Path
    [System.IO.File]::WriteAllText($fullPath, $updated, $utf8NoBom)
}

if ($SolutionContent) {
    & (Join-Path $scriptDir "replace_solution_region.ps1") `
        -JavaPath $JavaPath `
        -SolutionContent $SolutionContent
}

if ($NoteContent) {
    Update-MarkedMarkdownRegion -Path $NotePath -Content $NoteContent
}

$finishScript = Join-Path $scriptDir "finish_problem.ps1"
$finishArgs = @(
    "-JavaPath", $JavaPath,
    "-NotePath", $NotePath,
    "-ProblemTitle", $ProblemTitle,
    "-Thinking", $Thinking
)
if ($NoPush) {
    $finishArgs += "-NoPush"
}
& $finishScript @finishArgs

$branch = (& git branch --show-current).Trim()
$commit = (& git rev-parse --short HEAD).Trim()
$syncResult = "skipped"

if (-not $SkipSiyuan) {
    $inputPath = $SyncInputJson
    if (-not $inputPath) {
        $inputPath = Join-Path $env:TEMP ("leetcode-siyuan-sync-{0}.json" -f ([guid]::NewGuid().ToString("N")))
        $payloadArgs = @(
            (Join-Path $scriptDir "build_siyuan_payload.py"),
            "--output", $inputPath,
            "--problem-title", $ProblemTitle,
            "--thinking", $Thinking,
            "--commit", $commit
        )
        if ($StatementMarkdown) {
            $payloadArgs += @("--statement-markdown", $StatementMarkdown)
        }
        if ($ProcessMarkdown) {
            $payloadArgs += @("--process-markdown", $ProcessMarkdown)
        }
        if ($SolutionContent) {
            $payloadArgs += @("--solution-java", $SolutionContent)
        }
        if ($ComplexityMarkdown) {
            $payloadArgs += @("--complexity-markdown", $ComplexityMarkdown)
        }
        foreach ($pitfall in $Pitfalls) {
            if ($pitfall) {
                $payloadArgs += @("--pitfall", $pitfall)
            }
        }
        if ($TagPlanJson) {
            $payloadArgs += @("--tag-plan-json", $TagPlanJson)
        }
        if ($ReadinessJson) {
            $payloadArgs += @("--readiness-json", $ReadinessJson)
        }
        if ($ConversationDigestJson) {
            $payloadArgs += @("--conversation-digest-json", $ConversationDigestJson)
        }
        & python @payloadArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to build SiYuan sync payload with UTF-8 Python writer."
        }
    }

    $syncArgs = @((Join-Path $scriptDir "sync_leetcode_to_siyuan.py"), "--input", $inputPath)
    if ($WorkflowConfigPath) {
        $syncArgs += @("--config", $WorkflowConfigPath)
    }
    $dryRunOutput = & python @($syncArgs + "--dry-run") 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "SiYuan dry-run failed after Git completion:`n$($dryRunOutput -join "`n")"
    }
    $syncOutput = & python @syncArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "SiYuan sync failed after Git completion:`n$($syncOutput -join "`n")"
    }
    $syncResult = $syncOutput -join "`n"
}

[pscustomobject]@{
    branch = $branch
    commit = $commit
    pushed = (-not $NoPush)
    siyuanSync = $syncResult
} | ConvertTo-Json -Depth 10
