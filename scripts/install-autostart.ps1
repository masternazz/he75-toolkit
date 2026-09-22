<#
Run the per-game watcher (autogame.py) at every logon, hidden, as a per-user scheduled task. No admin needed.

  .\install-autostart.ps1                 # idle preset = reset (stock keys when no game is running)
  .\install-autostart.ps1 -Idle gaming    # idle preset = generic FPS setup
  .\install-autostart.ps1 -Remove         # uninstall
#>
param([ValidateSet('reset', 'gaming')][string]$Idle = 'reset', [switch]$Remove)

$name = 'HE75 Toolkit Auto-Switch'
if ($Remove) { Unregister-ScheduledTask -TaskName $name -Confirm:$false; "Removed '$name'."; return }

$repo = Split-Path -Parent $PSScriptRoot
$pythonw = (Get-Command pythonw.exe -ErrorAction Stop).Source        # windowless Python
$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$repo\autogame.py`" --idle $Idle" -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) `
  -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings -Force `
  -Description 'Applies HE75 hall-effect presets when a game starts (see the he75-toolkit repo).' | Out-Null
"Installed '$name': runs at logon as $env:USERNAME (idle preset: $Idle). Start it now with: Start-ScheduledTask '$name'"
