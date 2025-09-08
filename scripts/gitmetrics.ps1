# GitMetrics.ps1
Write-Host "Git Metrics for $(Split-Path -Leaf (Get-Location))"
Write-Host "--------------------------------------"

# Total commits
Write-Host "`nTotal commits:"
git rev-list --count HEAD

# Commits per author
Write-Host "`nCommits per author:"
git shortlog -s -n --all --no-merges

# First and last commit dates
Write-Host "`nFirst commit date:"
git log --reverse --format="%ad" --date=short | Select-Object -First 1

Write-Host "Last commit date:"
git log -1 --format="%ad" --date=short

# Active coding days
Write-Host "`nActive coding days:"
$dates = git log --date=short --pretty=format:"%ad" | Sort-Object | Get-Unique
$dates.Count

# Lines added and deleted
Write-Host "`nTotal lines added and deleted:"
$added = 0
$deleted = 0

git log --pretty=tformat: --numstat | ForEach-Object {
    $parts = $_ -split "`t"
    if ($parts.Length -ge 2 -and $parts[0] -match '^\d+$' -and $parts[1] -match '^\d+$') {
        $added += [int]$parts[0]
        $deleted += [int]$parts[1]
    }
}

Write-Host "Added: $added  Deleted: $deleted"

# Top modified files
Write-Host "`nTop 10 modified files:"
git log --pretty=format: --name-only | Where-Object { $_ -ne "" } |
    Group-Object | Sort-Object Count -Descending | Select-Object -First 10 |
    ForEach-Object { "$($_.Count) $($_.Name)" }

# Average commits per week
Write-Host "`nAverage commits per week:"
$weeks = git log --date=short --pretty=format:"%ad" | ForEach-Object {
    ($_ -split "-")[0..1] -join "-"
} | Sort-Object | Get-Unique
$totalCommits = git rev-list --count HEAD
$weekCount = $weeks.Count
$avg = [math]::Round($totalCommits / $weekCount, 2)
Write-Host "$avg commits/week (approx)"

Write-Host "--------------------------------------"
