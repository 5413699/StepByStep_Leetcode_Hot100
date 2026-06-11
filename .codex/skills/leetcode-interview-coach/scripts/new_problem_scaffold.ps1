param(
    [Parameter(Mandatory = $true)]
    [string]$NotePath,

    [Parameter(Mandatory = $true)]
    [string]$JavaPath,

    [Parameter(Mandatory = $true)]
    [string]$NoteContent,

    [Parameter(Mandatory = $true)]
    [string]$JavaContent
)

$ErrorActionPreference = "Stop"

function New-ScaffoldFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    if (Test-Path -LiteralPath $Path) {
        throw "Refusing to overwrite existing file: $Path"
    }

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    [System.IO.File]::WriteAllText($fullPath, $Content, $utf8NoBom)
}

New-ScaffoldFile -Path $NotePath -Content $NoteContent
New-ScaffoldFile -Path $JavaPath -Content $JavaContent

Write-Output "Created note: $NotePath"
Write-Output "Created Java: $JavaPath"
