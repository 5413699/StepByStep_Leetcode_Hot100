param(
    [Parameter(Mandatory = $true)]
    [string]$JavaPath,

    [Parameter(Mandatory = $true)]
    [string]$NotePath,

    [string]$ProblemTitle,

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
    [string]$WorkflowMetadataJson,
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

function Write-Utf8Json {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [object]$Value
    )

    $json = $Value | ConvertTo-Json -Depth 10
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json, $utf8NoBom)
}

if ($WorkflowMetadataJson) {
    $workflowMetadata = Read-Utf8JsonObject -Path $WorkflowMetadataJson
    if ($workflowMetadata.problemTitle) { $ProblemTitle = [string]$workflowMetadata.problemTitle }
    if ($workflowMetadata.thinking) { $Thinking = [string]$workflowMetadata.thinking }
    if ($workflowMetadata.solutionJava) { $SolutionContent = [string]$workflowMetadata.solutionJava }
    elseif ($workflowMetadata.solutionContent) { $SolutionContent = [string]$workflowMetadata.solutionContent }
    if ($workflowMetadata.noteContent) { $NoteContent = [string]$workflowMetadata.noteContent }
    if ($workflowMetadata.statementMarkdown) { $StatementMarkdown = [string]$workflowMetadata.statementMarkdown }
    if ($workflowMetadata.processMarkdown) { $ProcessMarkdown = [string]$workflowMetadata.processMarkdown }
    if ($workflowMetadata.complexityMarkdown) { $ComplexityMarkdown = [string]$workflowMetadata.complexityMarkdown }
    if ($workflowMetadata.pitfalls) { $Pitfalls = @($workflowMetadata.pitfalls | ForEach-Object { [string]$_ }) }
}

if (-not $ProblemTitle) {
    throw "ProblemTitle is required. Pass -ProblemTitle or provide problemTitle in -WorkflowMetadataJson."
}
if (-not $Thinking) {
    throw "Thinking is required. Pass -Thinking or provide thinking in -WorkflowMetadataJson."
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
$functionUsagePath = Join-Path $env:TEMP ("leetcode-function-usage-{0}.json" -f ([guid]::NewGuid().ToString("N")))
$functionNotePaths = @()
try {
    $functionArgs = @(
        (Join-Path $scriptDir "update_common_function_notes.py"),
        "--java-path", $JavaPath,
        "--problem-note", $NotePath,
        "--output-json", $functionUsagePath
    )
    if ($WorkflowMetadataJson) {
        $functionArgs += @("--workflow-metadata-json", $WorkflowMetadataJson)
    }
    if ($ProblemTitle) {
        $functionArgs += @("--problem-title", $ProblemTitle)
    }
    & python @functionArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to update common-function notes."
    }
    $functionUsage = Read-Utf8JsonObject -Path $functionUsagePath
    if ($functionUsage.updatedPaths) {
        $functionNotePaths = @($functionUsage.updatedPaths | ForEach-Object { [string]$_ })
    }
} catch {
    if (Test-Path -LiteralPath $functionUsagePath) {
        Remove-Item -LiteralPath $functionUsagePath -Force
    }
    throw
}

$commitMetadataPath = Join-Path $env:TEMP ("leetcode-commit-metadata-{0}.json" -f ([guid]::NewGuid().ToString("N")))
Write-Utf8Json -Path $commitMetadataPath -Value ([pscustomobject]@{
    problemTitle = $ProblemTitle
    thinking = $Thinking
})
$finishArgs = @{
    JavaPath = $JavaPath
    NotePath = $NotePath
    Paths = $functionNotePaths
    CommitMetadataJson = $commitMetadataPath
}
if ($NoPush) {
    $finishArgs.NoPush = $true
}
try {
    & $finishScript @finishArgs
} finally {
    if (Test-Path -LiteralPath $commitMetadataPath) {
        Remove-Item -LiteralPath $commitMetadataPath -Force
    }
}

$branch = (& git branch --show-current).Trim()
$commit = (& git rev-parse --short HEAD).Trim()
$syncResult = "skipped"

if (-not $SkipSiyuan) {
    $inputPath = $SyncInputJson
    if (-not $inputPath) {
        $inputPath = Join-Path $env:TEMP ("leetcode-siyuan-sync-{0}.json" -f ([guid]::NewGuid().ToString("N")))
        $payloadMetadataPath = Join-Path $env:TEMP ("leetcode-siyuan-metadata-{0}.json" -f ([guid]::NewGuid().ToString("N")))
        Write-Utf8Json -Path $payloadMetadataPath -Value ([pscustomobject]@{
            problemTitle = $ProblemTitle
            thinking = $Thinking
            commit = $commit
            statementMarkdown = $StatementMarkdown
            processMarkdown = $ProcessMarkdown
            solutionJava = $SolutionContent
            complexityMarkdown = $ComplexityMarkdown
            pitfalls = $Pitfalls
        })
        $payloadArgs = @(
            (Join-Path $scriptDir "build_siyuan_payload.py"),
            "--output", $inputPath,
            "--metadata-json", $payloadMetadataPath
        )
        if ($TagPlanJson) {
            $payloadArgs += @("--tag-plan-json", $TagPlanJson)
        }
        if ($ReadinessJson) {
            $payloadArgs += @("--readiness-json", $ReadinessJson)
        }
        if ($ConversationDigestJson) {
            $payloadArgs += @("--conversation-digest-json", $ConversationDigestJson)
        }
        if (Test-Path -LiteralPath $functionUsagePath) {
            $payloadArgs += @("--function-usage-json", $functionUsagePath)
        }
        try {
            & python @payloadArgs
        } finally {
            if (Test-Path -LiteralPath $payloadMetadataPath) {
                Remove-Item -LiteralPath $payloadMetadataPath -Force
            }
        }
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

if (Test-Path -LiteralPath $functionUsagePath) {
    Remove-Item -LiteralPath $functionUsagePath -Force
}

[pscustomobject]@{
    branch = $branch
    commit = $commit
    pushed = (-not $NoPush)
    siyuanSync = $syncResult
} | ConvertTo-Json -Depth 10
