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
    Set-Content -LiteralPath $Path -Value $updated -Encoding UTF8 -NoNewline
}

if ($SolutionContent) {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $scriptDir "replace_solution_region.ps1") `
        -JavaPath $JavaPath `
        -SolutionContent $SolutionContent
}

if ($NoteContent) {
    Update-MarkedMarkdownRegion -Path $NotePath -Content $NoteContent
}

$finishScript = Join-Path $scriptDir "finish_problem.ps1"
$finishArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $finishScript,
    "-Paths", $JavaPath, $NotePath,
    "-ProblemTitle", $ProblemTitle,
    "-Thinking", $Thinking
)
if ($NoPush) {
    $finishArgs += "-NoPush"
}
& powershell @finishArgs

$branch = (& git branch --show-current).Trim()
$commit = (& git rev-parse --short HEAD).Trim()
$syncResult = "skipped"

if (-not $SkipSiyuan) {
    $inputPath = $SyncInputJson
    if (-not $inputPath) {
        $tagPlan = $null
        if ($TagPlanJson) {
            $tagPlan = Get-Content -LiteralPath $TagPlanJson -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        $conversationDigest = $null
        if ($ConversationDigestJson) {
            $conversationDigest = Get-Content -LiteralPath $ConversationDigestJson -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        $payload = [ordered]@{
            problemTitle = $ProblemTitle
            statementMarkdown = $StatementMarkdown
            thinkingMarkdown = $Thinking
            processMarkdown = $ProcessMarkdown
            solutionJava = $SolutionContent
            complexityMarkdown = $ComplexityMarkdown
            pitfalls = $Pitfalls
            tags = $(if ($tagPlan -and $tagPlan.tags) { $tagPlan.tags } else { @{} })
            tagEvidence = $(if ($tagPlan -and $tagPlan.tagEvidence) { $tagPlan.tagEvidence } else { @{} })
            readiness = $(if ($ReadinessJson) { Get-Content -LiteralPath $ReadinessJson -Raw -Encoding UTF8 | ConvertFrom-Json } else { @{} })
            conversationDigest = $(if ($conversationDigest) { $conversationDigest } else { @{} })
            git = @{
                branch = $branch
                commit = $commit
            }
        }
        $inputPath = Join-Path $env:TEMP ("leetcode-siyuan-sync-{0}.json" -f ([guid]::NewGuid().ToString("N")))
        $payload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $inputPath -Encoding UTF8
    }

    $syncArgs = @((Join-Path $scriptDir "sync_leetcode_to_siyuan.py"), "--input", $inputPath)
    if ($WorkflowConfigPath) {
        $syncArgs += @("--config", $WorkflowConfigPath)
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
