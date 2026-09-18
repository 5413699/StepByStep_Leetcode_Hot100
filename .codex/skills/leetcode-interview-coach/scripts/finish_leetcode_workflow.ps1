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
    [string]$StatusJson,
    [string[]]$AdditionalPaths = @(),
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

    $json = $Value | ConvertTo-Json -Depth 30
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json, $utf8NoBom)
}

# Persist evidence even when an exception interrupts the workflow. A successful
# write is deliberately separate from directory, read-back and browser checks.
if (-not $StatusJson) {
    $StatusJson = Join-Path $env:TEMP ("leetcode-closeout-{0}.json" -f ([guid]::NewGuid().ToString("N")))
}
$StatusJson = [System.IO.Path]::GetFullPath($StatusJson)
$report = [ordered]@{
    schemaVersion = 1
    workflowId = [guid]::NewGuid().ToString("N")
    status = "incomplete"
    complete = $false
    stages = [ordered]@{}
    providers = [ordered]@{}
    failures = @()
    statusPath = $StatusJson
}
foreach ($name in @("configuration", "record", "local", "commit", "push")) {
    $report.stages[$name] = @{status = "pending"; evidence = $null}
}
$currentStage = "configuration"
try {
$configPath = $WorkflowConfigPath
if (-not $configPath) { $configPath = Join-Path $env:USERPROFILE ".codex\leetcode-hot100-workflow.local.json" }
if (-not (Test-Path -LiteralPath $configPath)) {
    throw "Workflow configuration is missing: $configPath. Resolve publishing targets before claiming a complete closeout."
}
$workflowConfig = Read-Utf8JsonObject -Path $configPath
foreach ($name in @("siyuan", "yuque")) {
    $settings = $workflowConfig.$name
    if (-not $settings -or $null -eq $settings.enabled) {
        throw "Workflow configuration must explicitly declare $name.enabled; an absent provider is not an explicit opt-out."
    }
    $stages = [ordered]@{}
    foreach ($step in @("dryRun", "write", "directory", "readback")) {
        $stages[$step] = @{status = "pending"; evidence = $null}
    }
    if ($name -eq "yuque") { $stages.browser = @{status = "pending"; evidence = $null} }
    $report.providers[$name] = @{enabled = [bool]$settings.enabled; stages = $stages}
}
$report.stages.configuration = @{status = "passed"; evidence = @{path = [System.IO.Path]::GetFullPath($configPath)}}
Write-Utf8Json -Path $StatusJson -Value $report
$currentStage = "record"
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
$report.payloadPath = $inputPath
& python (Join-Path $scriptDir "check_closeout.py") --validate-record $inputPath --java-path $JavaPath
if ($LASTEXITCODE -ne 0) { throw "Learning record validation failed; recover source material or explicitly label missing history." }
$report.stages.record = @{status = "passed"; evidence = @{payloadPath = $inputPath; javaPath = $JavaPath; codeAlignment = "matched"}}
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
$report.notePreviewPath = $renderedNotePath
$currentStage = "local"
Write-Utf8Json -Path $StatusJson -Value $report

$commitMetadataPath = Join-Path $env:TEMP ("leetcode-commit-metadata-{0}.json" -f ([guid]::NewGuid().ToString("N")))
Write-Utf8Json -Path $commitMetadataPath -Value ([pscustomobject]@{
    problemTitle = $ProblemTitle
    thinking = $Thinking
})
$finishArgs = @{
    JavaPath = $JavaPath
    NotePath = $NotePath
    Paths = @($functionNotePaths) + @($AdditionalPaths)
    CommitMetadataJson = $commitMetadataPath
    NoPush = $true
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
$commit = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or -not $commit) { throw "Cannot verify the local commit." }
$report.branch = $branch
$report.commit = $commit
$report.stages.local = @{status = "passed"; evidence = @{maven = "mvn -q -DskipTests compile"; previewPath = $renderedNotePath; javaPath = $JavaPath; notePath = $NotePath}}
$report.stages.commit = @{status = "passed"; evidence = @{commit = $commit; paths = @($JavaPath, $NotePath) + @($functionNotePaths) + @($AdditionalPaths)}}
$currentStage = "push"
if ($NoPush) {
    $report.stages.push = @{status = "skipped"; evidence = "-NoPush was explicitly supplied; full closeout remains incomplete."}
} else {
    $remote = (& git config "branch.$branch.remote")
    if (-not $remote) { $remote = "origin" }
    $remote = ([string]$remote).Trim()
    $remoteRef = (& git config "branch.$branch.merge")
    if (-not $remoteRef) { $remoteRef = "refs/heads/$branch" }
    $remoteRef = ([string]$remoteRef).Trim()
    & git push -u $remote "HEAD:$remoteRef"
    if ($LASTEXITCODE -ne 0) { throw "Git push failed; local commit is retained." }
    $remoteOutput = & git ls-remote --exit-code $remote $remoteRef
    if ($LASTEXITCODE -ne 0 -or -not $remoteOutput -or (($remoteOutput -split '\s+')[0] -ne $commit)) {
        throw "Remote branch does not confirm the pushed commit."
    }
    $report.stages.push = @{status = "passed"; evidence = @{remote = $remote; ref = ([string]$remoteRef).Trim(); commit = $commit}}
}
$report.pushed = ($report.stages.push.status -eq "passed")
$currentStage = "record"
# Only generated Git metadata changes after commit; the authored body is reused.
$learningRecord = Read-Utf8JsonObject -Path $inputPath
$learningRecord | Add-Member -NotePropertyName git -NotePropertyValue ([pscustomobject]@{commit = $commit}) -Force
Write-Utf8Json -Path $inputPath -Value $learningRecord
$sha256 = [System.Security.Cryptography.SHA256]::Create()
try {
    $report.payloadSha256 = [System.BitConverter]::ToString($sha256.ComputeHash([System.IO.File]::ReadAllBytes($inputPath))).Replace("-", "").ToLowerInvariant()
} finally { $sha256.Dispose() }
$currentStage = "providers"
$syncResult = "skipped"
$yuqueResult = "skipped"
$providerFailures = @()

$siyuanEnabled = $report.providers.siyuan.enabled -and (-not $SkipSiyuan)
$yuqueEnabled = $report.providers.yuque.enabled -and (-not $SkipYuque)
if ($workflowConfig.yuque -and $null -ne $workflowConfig.yuque.autoPublish -and -not $workflowConfig.yuque.autoPublish) { $yuqueEnabled = $false }
foreach ($name in @("siyuan", "yuque")) {
    $willRun = if ($name -eq "siyuan") { $siyuanEnabled } else { $yuqueEnabled }
    if ($report.providers[$name].enabled -and -not $willRun) {
        foreach ($step in @($report.providers[$name].stages.Keys)) {
            $report.providers[$name].stages[$step] = @{status = "skipped"; evidence = "Skipped by switch or autoPublish=false; enabled target remains incomplete."}
        }
    }
}
Write-Utf8Json -Path $StatusJson -Value $report

if ($siyuanEnabled) {
    $syncArgs = @((Join-Path $scriptDir "sync_leetcode_to_siyuan.py"), "--input", $inputPath)
    if ($configPath) {
        $syncArgs += @("--config", $configPath)
    }
    $providerStep = "dryRun"
    try {
        $dryRunOutput = & python @($syncArgs + "--dry-run") 2>&1
        if ($LASTEXITCODE -ne 0) { throw "SiYuan dry-run failed:`n$($dryRunOutput -join "`n")" }
        $siyuanDryRun = ($dryRunOutput -join "`n") | ConvertFrom-Json
        if (-not $siyuanDryRun.dryRun -or -not $siyuanDryRun.problem) { throw "SiYuan response does not confirm a read-only dry-run." }
        $report.providers.siyuan.stages.dryRun = @{status = "passed"; evidence = $siyuanDryRun}
        $providerStep = "write"
        Write-Utf8Json -Path $StatusJson -Value $report
        $syncOutput = & python @syncArgs 2>&1
        if ($LASTEXITCODE -ne 0) { throw "SiYuan sync failed:`n$($syncOutput -join "`n")" }
        $syncResult = ($syncOutput -join "`n") | ConvertFrom-Json
        if (-not $syncResult.enabled -or $syncResult.validation -ne "passed" -or -not $syncResult.problem.id) { throw "SiYuan response does not confirm publication and validation." }
        foreach ($step in @("write", "directory", "readback")) {
            $report.providers.siyuan.stages[$step] = @{status = "passed"; evidence = $syncResult}
        }
    } catch {
        $syncResult = "failed"
        $state = if ($providerStep -eq "write") { "uncertain" } else { "failed" }
        $report.providers.siyuan.stages[$providerStep] = @{status = $state; evidence = $_.Exception.Message}
        $providerFailures += "SiYuan: $($_.Exception.Message)"
    }
    $report.siyuanSync = $syncResult
    $report.failures = $providerFailures
    Write-Utf8Json -Path $StatusJson -Value $report
}

if ($yuqueEnabled) {
    $yuqueArgs = @((Join-Path $scriptDir "sync_leetcode_to_yuque.py"), "--input", $inputPath)
    if ($configPath) { $yuqueArgs += @("--config", $configPath) }
    $providerStep = "dryRun"
    try {
        $yuqueDryRunOutput = & python @($yuqueArgs + "--dry-run") 2>&1
        if ($LASTEXITCODE -ne 0) { throw "YuQue dry-run failed:`n$($yuqueDryRunOutput -join "`n")" }
        $yuqueDryRun = ($yuqueDryRunOutput -join "`n") | ConvertFrom-Json
        if (-not $yuqueDryRun.enabled -or -not $yuqueDryRun.dryRun -or -not $yuqueDryRun.success) { throw "YuQue response does not confirm a read-only dry-run." }
        $report.providers.yuque.stages.dryRun = @{status = "passed"; evidence = $yuqueDryRun}
        $report.providers.yuque.url = $yuqueDryRun.url
        $providerStep = "write"
        Write-Utf8Json -Path $StatusJson -Value $report
        $yuqueOutput = & python @yuqueArgs 2>&1
        $yuqueExitCode = $LASTEXITCODE
        $yuqueText = $yuqueOutput -join "`n"
        try { $yuqueResult = $yuqueText | ConvertFrom-Json } catch { $yuqueResult = $yuqueText }
        $report.providers.yuque.url = $yuqueResult.url
        $statusFields = @{write = "writeStatus"; directory = "directoryStatus"; readback = "verificationStatus"}
        foreach ($step in @("write", "directory", "readback")) {
            $observed = [string]$yuqueResult.($statusFields[$step])
            $expected = if ($step -eq "write") { "written" } else { "verified" }
            $state = if ($observed -eq $expected) { "passed" } elseif ($observed) { $observed } else { "failed" }
            $report.providers.yuque.stages[$step] = @{status = $state; evidence = $yuqueResult}
        }
        if ($yuqueExitCode -ne 0) { $providerFailures += "YuQue: publication incomplete; inspect yuqueSync statuses." }
    } catch {
        $yuqueResult = "failed"
        $state = if ($providerStep -eq "write") { "uncertain" } else { "failed" }
        $report.providers.yuque.stages[$providerStep] = @{status = $state; evidence = $_.Exception.Message}
        $providerFailures += "YuQue: $($_.Exception.Message)"
    }
}

if (Test-Path -LiteralPath $functionUsagePath) {
    Remove-Item -LiteralPath $functionUsagePath -Force
}

$report.siyuanSync = $syncResult
$report.yuqueSync = $yuqueResult
$report.failures = $providerFailures
} catch {
    $report.failures += $_.Exception.Message
    if ($report.stages.Contains($currentStage)) { $report.stages[$currentStage] = @{status = "failed"; evidence = $_.Exception.Message} }
    else { $report.fatalError = $_.Exception.Message }
} finally {
    Write-Utf8Json -Path $StatusJson -Value $report
}
# Browser evidence is recorded afterwards via check_closeout.py. Do not rerun
# this writing workflow merely to mark the already published page verified.
& python (Join-Path $scriptDir "check_closeout.py") --report $StatusJson
$closeoutExitCode = $LASTEXITCODE
if ($closeoutExitCode -ne 0) { throw "Closeout is incomplete. Inspect $StatusJson; continue only missing checks, never repeat an uncertain create." }
