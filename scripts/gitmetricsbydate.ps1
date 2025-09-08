param (
    [Parameter(Mandatory=$true)]
    [datetime]$StartDate,

    [Parameter(Mandatory=$true)]
    [datetime]$EndDate,

    [string]$OutputFile = "GitMetricsReport.md"
)

$repoName = Split-Path -Leaf (Get-Location)
$gitStart = $StartDate.ToString("yyyy-MM-dd")
$gitEnd = $EndDate.ToString("yyyy-MM-dd")

$md = @()
$md += "# Git Metrics Report"
$md += '**Repository:** `' + $repoName + '`'
$md += '**Date Range:** `' + $gitStart + '` to `' + $gitEnd + '`'
$md += "---"

# Get commits
$commits = git log --since="$gitStart" --until="$gitEnd" --pretty=format:"%H|%an|%ad" --date=short
$totalCommits = $commits.Count
$md += "`n## Total Commits"
$md += "$totalCommits"

# Commits per author
$md += "`n## Commits per Author"
$md += "| Author | Commits |"
$md += "|--------|---------|"
$commits | ForEach-Object { ($_ -split "\|")[1] } |
    Group-Object | Sort-Object Count -Descending | ForEach-Object {
        $md += "| $($_.Name) | $($_.Count) |"
    }

# Active coding days
$dates = $commits | ForEach-Object { ($_ -split "\|")[2] } | Sort-Object | Get-Unique
$md += "`n## Active Coding Days"
$md += "$($dates.Count)"

# Lines added and deleted
$added = 0
$deleted = 0
$commitHashes = $commits | ForEach-Object { ($_ -split "\|")[0] }

foreach ($hash in $commitHashes) {
    git show --numstat --format=tformat: $hash | ForEach-Object {
        $parts = $_ -split "`t"
        if ($parts.Length -ge 2 -and $parts[0] -match '^\d+$' -and $parts[1] -match '^\d+$') {
            $added += [int]$parts[0]
            $deleted += [int]$parts[1]
        }
    }
}

$md += "`n## Lines Added and Deleted"
$md += "| Metric | Count |"
$md += "|--------|-------|"
$md += "| Added | $added |"
$md += "| Deleted | $deleted |"

# Top modified files
$files = @()
foreach ($hash in $commitHashes) {
    $files += git show --pretty=format: --name-only $hash
}
$md += "`n## Top 10 Modified Files"
$md += "| File | Modifications |"
$md += "|------|---------------|"
$files | Where-Object { $_ -ne "" } | Group-Object | Sort-Object Count -Descending | Select-Object -First 10 |
    ForEach-Object {
        $md += "| $($_.Name) | $($_.Count) |"
    }

# Write to file
$md | Set-Content $OutputFile
Write-Host "Markdown report saved to $OutputFile"