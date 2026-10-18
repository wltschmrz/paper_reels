param([string]$DevContainer='cuda13-dev',[string]$Repo='/workspace/mvp/paper_reels')
$ErrorActionPreference='Stop'
$work=Join-Path $env:TEMP ('scholarshorts-render-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path "$work/context/pipeline" -Force | Out-Null
function Invoke-Docker {
  param([string[]]$DockerArgs)
  & docker @DockerArgs
  if ($LASTEXITCODE -ne 0) { throw "Docker failed: $($DockerArgs[0])" }
}
Invoke-Docker -DockerArgs @('cp',"${DevContainer}:$Repo/backend/tools/Dockerfile.render","$work/context/Dockerfile")
Invoke-Docker -DockerArgs @('cp',"${DevContainer}:$Repo/backend/pipeline/render_kit","$work/context/pipeline/render_kit")
Write-Host 'Building isolated renderer (first run can take several minutes)...'
Invoke-Docker -DockerArgs @('build','-t','scholarshorts-render:local',"$work/context")
Write-Host 'Renderer connected. Leave this PowerShell window open. Ctrl+C stops the bridge.'
try {
 while ($true) {
  $raw=& docker exec $DevContainer "$Repo/.venv/bin/python" "$Repo/backend/tools/bridge_queue.py"
  if ($LASTEXITCODE -ne 0) {throw 'Cannot read development container queue'}
  if (-not $raw) {Start-Sleep -Seconds 2;continue}
  $r=$raw | ConvertFrom-Json
  $ticket=[string]$r.ticket; $sid=[string]$r.sid; $quality=[string]$r.quality
  if ($ticket -notmatch '^[a-f0-9]{32}$' -or $sid -notmatch '^S\d{1,2}$' -or $quality -notin @('preview','final')) {throw 'Invalid render request'}
  $dir=Join-Path $work $ticket
  New-Item -ItemType Directory -Path "$dir/render" -Force | Out-Null
  $queue="$Repo/backend/data/render-bridge/$ticket"
  Invoke-Docker -DockerArgs @('cp',"${DevContainer}:$queue/input","$dir/input")
  New-Item -ItemType Directory -Path "$dir/input/render" -Force | Out-Null
  $name="ss-render-$ticket"
  $exit=1; $log=''
  try {
   Invoke-Docker -DockerArgs @('create','--name',$name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--cpus','2','--memory','3g','--pids-limit','128','--user','65534:65534','--tmpfs','/tmp:rw,size=512m','--mount',"type=bind,source=$dir/input,target=/job,readonly",'--mount',"type=bind,source=$dir/render,target=/job/render",'-e','SS_JOB_DIR=/job','-e','PYTHONPATH=/job/runtime:/app/pipeline:/job/scenes','-e','HOME=/tmp','scholarshorts-render:local','manim','-r',[string]$r.resolution,'--fps',[string]$r.fps,'--disable_caching','--media_dir',"/job/render/_media/$quality/$sid",'-o',"$sid.mp4","/job/scenes/$sid.py",$sid) | Out-Null
   Invoke-Docker -DockerArgs @('start',$name) | Out-Null
   $deadline=(Get-Date).AddSeconds([Math]::Min(900,[int]$r.timeout))
   while ((& docker inspect -f '{{.State.Running}}' $name) -eq 'true') {
    if ((Get-Date) -gt $deadline) {& docker kill $name | Out-Null;break}
    Start-Sleep -Seconds 2
   }
   $exit=[int](& docker inspect -f '{{.State.ExitCode}}' $name)
   $previousPreference=$ErrorActionPreference
   $ErrorActionPreference="Continue"
   $log=(& docker logs $name 2>&1 | Out-String)
   $ErrorActionPreference=$previousPreference
   if ($log.Length -gt 6000) {$log=$log.Substring($log.Length-6000)}
   if ($exit -eq 0) {Invoke-Docker -DockerArgs @('cp',"$dir/render","${DevContainer}:$queue/output")}
  } catch {$log=$_.ToString();$exit=1} finally {& docker rm -f $name 2>$null | Out-Null}
  @{returncode=$exit;stderr=$log} | ConvertTo-Json -Compress | Set-Content -Encoding UTF8 "$dir/result.json"
  Invoke-Docker -DockerArgs @('cp',"$dir/result.json","${DevContainer}:$queue/result.json")
  Write-Host "$quality $sid finished (exit $exit)"
 }
} finally {Write-Host "Renderer stopped. Temporary files: $work"}
