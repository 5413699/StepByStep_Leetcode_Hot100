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
    [switch]$ReplaceWholeNote,
    [switch]$AllowUnrelatedChanges,
    [switch]$SkipSiyuan,
    [switch]$SkipYuque,
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
    $fullPath = [System.IO.Path]::GetFullPath($Path)
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

# Build the authored learning record once, before rendering or committing.
# Preserve optional nested teaching fields from the UTF-8 metadata verbatim.
$inputPath = Join-Path $env:TEMP ("leetcode-learning-record-{0}.json" -f ([guid]::NewGuid().ToString("N")))
if ($SyncInputJson) {
    # The user's source record is immutable; generated Git metadata belongs to
    # the run's copy, so it cannot dirty a committed fixture after the commit.
    Copy-Item -LiteralPath $SyncInputJson -Destination $inputPath
} else {
    $payloadMetadataPath = Join-Path $env:TEMP ("leetcode-learning-record-metadata-{0}.json" -f ([guid]::NewGuid().ToString("N")))
    $recordMetadata = @{}
    if ($workflowMetadata) {
        foreach ($property in $workflowMetadata.PSObject.Properties) {
            $recordMetadata[$property.Name] = $property.Value
        }
    }
    $recordMetadata.problemTitle = $ProblemTitle
    $recordMetadata.thinking = $Thinking
    $recordMetadata.noteContent = $NoteContent
    $recordMetadata.statementMarkdown = $StatementMarkdown
    $recordMetadata.processMarkdown = $ProcessMarkdown
    $recordMetadata.solutionJava = $SolutionContent
    $recordMetadata.complexityMarkdown = $ComplexityMarkdown
    $recordMetadata.pitfalls = $Pitfalls
    Write-Utf8Json -Path $payloadMetadataPath -Value $recordMetadata
    $payloadArgs = @((Join-Path $scriptDir "build_siyuan_payload.py"), "--output", $inputPath, "--metadata-json", $payloadMetadataPath)
    if ($TagPlanJson) { $payloadArgs += @("--tag-plan-json", $TagPlanJson) }
    if ($ReadinessJson) { $payloadArgs += @("--readiness-json", $ReadinessJson) }
    if ($ConversationDigestJson) { $payloadArgs += @("--conversation-digest-json", $ConversationDigestJson) }
    if (Test-Path -LiteralPath $functionUsagePath) { $payloadArgs += @("--function-usage-json", $functionUsagePath) }
    try {
        & python @payloadArgs
        if ($LASTEXITCODE -ne 0) { throw "Failed to build provider-neutral learning-record payload." }
    } finally {
        if (Test-Path -LiteralPath $payloadMetadataPath) { Remove-Item -LiteralPath $payloadMetadataPath -Force }
    }
}
$renderedNotePath = Join-Path $env:TEMP ("leetcode-note-preview-{0}.md" -f ([guid]::NewGuid().ToString("N")))
$renderArgs = @((Join-Path $scriptDir "render_learning_note.py"), "--input", $inputPath, "--output", $renderedNotePath)
if (-not $ReplaceWholeNote) { $renderArgs += "--without-title" }
& python @renderArgs
if ($LASTEXITCODE -ne 0) { throw "Learning note rendering failed; retained payload: $inputPath" }
$renderedNote = [System.IO.File]::ReadAllText($renderedNotePath, [System.Text.UTF8Encoding]::new($false, $true))
if ($ReplaceWholeNote) {
    [System.IO.File]::WriteAllText([System.IO.Path]::GetFullPath($NotePath), $renderedNote, [System.Text.UTF8Encoding]::new($false))
} else {
    Update-MarkedMarkdownRegion -Path $NotePath -Content $renderedNote
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
if ($AllowUnrelatedChanges) { $finishArgs.AllowUnrelatedChanges = $true }
try {
    & $finishScript @finishArgs
} finally {
    if (Test-Path -LiteralPath $commitMetadataPath) {
        Remove-Item -LiteralPath $commitMetadataPath -Force
    }
}

$branch = (& git branch --show-current).Trim()
$commit = (& git rev-parse --short HEAD).Trim()
# Only generated Git metadata changes after commit; the authored body is reused.
$learningRecord = Read-Utf8JsonObject -Path $inputPath
$learningRecord | Add-Member -NotePropertyName git -NotePropertyValue ([pscustomobject]@{commit = $commit}) -Force
Write-Utf8Json -Path $inputPath -Value $learningRecord
$syncResult = "skipped"
$yuqueResult = "skipped"
$providerFailures = @()

$configPath = $WorkflowConfigPath
if (-not $configPath) {
    $configPath = Join-Path $env:USERPROFILE ".codex\leetcode-hot100-workflow.local.json"
}
$workflowConfig = $null
if (Test-Path -LiteralPath $configPath) {
    $workflowConfig = Read-Utf8JsonObject -Path $configPath
}
$siyuanEnabled = -not $SkipSiyuan
$yuqueEnabled = (-not $SkipYuque) -and $workflowConfig -and $workflowConfig.yuque -and [bool]$workflowConfig.yuque.enabled
if ($workflowConfig -and $workflowConfig.siyuan -and $null -ne $workflowConfig.siyuan.enabled) {
    $siyuanEnabled = $siyuanEnabled -and [bool]$workflowConfig.siyuan.enabled
}
if ($workflowConfig -and $workflowConfig.yuque -and $null -ne $workflowConfig.yuque.enabled) {
    $yuqueEnabled = $yuqueEnabled -and [bool]$workflowConfig.yuque.enabled
}
if ($workflowConfig -and $workflowConfig.yuque -and $null -ne $workflowConfig.yuque.autoPublish) {
    $yuqueEnabled = $yuqueEnabled -and [bool]$workflowConfig.yuque.autoPublish
}

if ($siyuanEnabled) {
    $syncArgs = @((Join-Path $scriptDir "sync_leetcode_to_siyuan.py"), "--input", $inputPath)
    if ($configPath) {
        $syncArgs += @("--config", $configPath)
    }
    try {
        $dryRunOutput = & python @($syncArgs + "--dry-run") 2>&1
        if ($LASTEXITCODE -ne 0) { throw "SiYuan dry-run failed:`n$($dryRunOutput -join "`n")" }
        $syncOutput = & python @syncArgs 2>&1
        if ($LASTEXITCODE -ne 0) { throw "SiYuan sync failed:`n$($syncOutput -join "`n")" }
        $syncResult = $syncOutput -join "`n"
    } catch {
        $syncResult = "failed"
        $providerFailures += "SiYuan: $($_.Exception.Message)"
    }
}

if ($yuqueEnabled) {
    $yuqueArgs = @((Join-Path $scriptDir "sync_leetcode_to_yuque.py"), "--input", $inputPath)
    if ($configPath) { $yuqueArgs += @("--config", $configPath) }
    try {
        $yuqueDryRunOutput = & python @($yuqueArgs + "--dry-run") 2>&1
        if ($LASTEXITCODE -ne 0) { throw "YuQue dry-run failed:`n$($yuqueDryRunOutput -join "`n")" }
        $yuqueOutput = & python @yuqueArgs 2>&1
        $yuqueExitCode = $LASTEXITCODE
        $yuqueText = $yuqueOutput -join "`n"
        try { $yuqueResult = $yuqueText | ConvertFrom-Json } catch { $yuqueResult = $yuqueText }
        if ($yuqueExitCode -ne 0) { $providerFailures += "YuQue: publication incomplete; inspect yuqueSync statuses." }
    } catch {
        $yuqueResult = "failed"
        $providerFailures += "YuQue: $($_.Exception.Message)"
    }
}

if (Test-Path -LiteralPath $functionUsagePath) {
    Remove-Item -LiteralPath $functionUsagePath -Force
}

[pscustomobject]@{
    branch = $branch
    commit = $commit
    pushed = (-not $NoPush)
    siyuanSync = $syncResult
    yuqueSync = $yuqueResult
    payloadPath = $inputPath
    notePreviewPath = $renderedNotePath
    failures = $providerFailures
} | ConvertTo-Json -Depth 10
