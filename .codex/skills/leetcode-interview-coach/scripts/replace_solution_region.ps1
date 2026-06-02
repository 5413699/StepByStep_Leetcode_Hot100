param(
    [Parameter(Mandatory = $true)]
    [string]$JavaPath,

    [Parameter(Mandatory = $true)]
    [string]$SolutionContent
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $JavaPath)) {
    throw "Java file does not exist: $JavaPath"
}

$content = Get-Content -LiteralPath $JavaPath -Raw -Encoding UTF8
$startMarker = "    // region LeetCode solution"
$endMarker = "    // endregion"

$startIndex = $content.IndexOf($startMarker)
$endIndex = $content.IndexOf($endMarker)

if ($startIndex -lt 0 -or $endIndex -lt 0 -or $endIndex -le $startIndex) {
    throw "Solution region markers were not found or are malformed in $JavaPath."
}

$lineEnding = "`n"
if ($content.Contains("`r`n")) {
    $lineEnding = "`r`n"
}

$normalizedSolution = ($SolutionContent -replace "`r`n|`r|`n", $lineEnding).TrimEnd()
$replacement = $startMarker + $lineEnding + $normalizedSolution + $lineEnding + $endMarker

$newContent = $content.Substring(0, $startIndex) +
    $replacement +
    $content.Substring($endIndex + $endMarker.Length)

Set-Content -LiteralPath $JavaPath -Value $newContent -Encoding UTF8 -NoNewline
Write-Output "Updated solution region: $JavaPath"
