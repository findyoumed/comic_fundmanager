param([switch]$Check)
# [LOG: 20261114_1529] UTF-8 인코딩 설정 (한글 경로 깨짐 방지)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
$expectedRemote = 'https://github.com/findyoumed/comic_fundmanager.git'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$step = 'preflight'

function Invoke-ProjectGit {
    param([string[]]$GitArguments)
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & git @GitArguments
    $gitExit = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference
    if ($gitExit -ne 0) { throw "git $($GitArguments -join ' ') failed (exit $gitExit)." }
}

Push-Location -LiteralPath $projectRoot
try {
    Write-Host '[1/6] Checking repository and upload files...'
    Get-Command git -ErrorAction Stop | Out-Null
    # [LOG: 20261114_1529] 한글 경로 인코딩 보존
    $actualRoot = (& git -c core.quotepath=false rev-parse --show-toplevel).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'This folder is not a Git repository.' }
    if ([IO.Path]::GetFullPath($actualRoot) -ine $projectRoot) { throw 'Unexpected repository root.' }
    $remote = & git remote get-url origin
    if ($LASTEXITCODE -ne 0 -or $remote -ne $expectedRemote) { throw "Expected origin: $expectedRemote ; configured: $remote" }
    $branch = & git branch --show-current
    if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') { throw "Expected branch main; current branch: $branch" }
    $changedPaths = @(& git -c core.quotepath=false status --porcelain=v1)
    if ($LASTEXITCODE -ne 0) { throw 'Could not read Git status.' }
    Write-Host "Repository: $projectRoot"
    Write-Host "Changed paths: $($changedPaths.Count)"
    $candidatePaths = @(& git -c core.quotepath=false ls-files --cached --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) { throw 'Could not inspect upload files.' }
    $largeFiles = @($candidatePaths | Select-Object -Unique | ForEach-Object {
        if (Test-Path -LiteralPath $_ -PathType Leaf) {
            $item = Get-Item -LiteralPath $_
            if ($item.Length -ge 100MB) { $item.FullName }
        }
    })
    if ($largeFiles.Count) { throw "Files at or above 100 MiB must be excluded or stored with Git LFS: $($largeFiles -join ', ')" }
    if ($Check) {
        Write-Host 'CHECK PASSED. No staging, commit, network request or push performed.'
        exit 0
    }
    $env:GIT_TERMINAL_PROMPT = '0'
    $env:GCM_INTERACTIVE = 'Never'
    $networkOptions = @('-c','credential.interactive=false','-c','http.lowSpeedLimit=1024','-c','http.lowSpeedTime=60')
    $step = 'fetch/authentication'
    Write-Host '[2/6] Fetching GitHub with visible progress (slow connections time out)...'
    Invoke-ProjectGit -GitArguments ($networkOptions + @('fetch','--progress','origin'))
    $step = 'staging'
    Write-Host '[3/6] Staging project changes...'
    Invoke-ProjectGit -GitArguments @('add','-A')
    & git diff --cached --quiet
    $diffExit = $LASTEXITCODE
    if ($diffExit -gt 1) { throw 'Could not inspect staged changes.' }
    $step = 'commit'
    Write-Host '[4/6] Saving local commit...'
    if ($diffExit -eq 1) {
        Invoke-ProjectGit -GitArguments @('commit','-m',('Update comic project ' + (Get-Date -Format 'yyyy-MM-dd HH:mm')))
    } else { Write-Host 'No new local changes to commit.' }
    $step = 'branch synchronization'
    Write-Host '[5/6] Checking branch synchronization...'
    & git show-ref --verify --quiet refs/remotes/origin/main
    if ($LASTEXITCODE -eq 0) {
        $counts = & git rev-list --left-right --count main...origin/main
        if ($LASTEXITCODE -ne 0) { throw 'Could not compare local and remote branches.' }
        $parts = $counts.Trim() -split '\s+'
        $ahead = [int]$parts[0]
        $behind = [int]$parts[1]
        if ($ahead -gt 0 -and $behind -gt 0) { throw 'Local and GitHub main have diverged. Local changes are saved; merge branches before pushing. No force push was attempted.' }
        if ($behind -gt 0) { Invoke-ProjectGit -GitArguments @('merge','--ff-only','origin/main') }
    }
    $step = 'push'
    Write-Host '[6/6] Uploading to GitHub...'
    Invoke-ProjectGit -GitArguments ($networkOptions + @('push','--progress','-u','origin','main'))
    Write-Host 'SUCCESS: local commit saved and GitHub upload completed.' -ForegroundColor Green
    exit 0
} catch {
    Write-Host "FAILED at step: $step" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($step -eq 'fetch/authentication' -or $step -eq 'push') {
        Write-Host 'For an authentication error, sign in using Git Credential Manager or GitHub CLI, then run this file again.'
    }
    exit 1
} finally { Pop-Location }
