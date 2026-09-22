<#
Set lighting on an EPOMAKER HE75 V2 (VID 3151 PID 5054) with no driver app.
Protocol (RY5088): feature report 0, 64 bytes: 07 mode (4-speed) brightness flags R G B checksum
  checksum = 0xFF - (sum of bytes 0..7); flags = 7 normal color / 8 rainbow. Stored on the board.
Source: ramarivera/epomaker-driver-linux (docs/he75-v2.md, codec.py), matched against a live capture.
  .\kb-light.ps1 -Mode ripple -Color 8A2BE2        # spread purple
  .\kb-light.ps1 -Mode reactive -Color 8A2BE2      # lights only under pressed keys
  .\kb-light.ps1 -Read                             # print current setting
#>
param(
  [string]$Mode = 'ripple', [string]$Color = '8A2BE2',
  [ValidateRange(0,4)][int]$Brightness = 4, [ValidateRange(0,4)][int]$Speed = 4,
  [switch]$Rainbow, [switch]$Read, [switch]$Side   # -Side = the light bar (modes: off solid neon wave)
)
$modes = @{ off=0; solid=1; breathing=2; neon=3; wave=4; ripple=5; raindrop=6; snake=7; reactive=8; convergence=9
  sine=10; kaleidoscope=11; 'line-wave'=12; laser=14; 'circle-wave'=15; dazzling=16; rain=17; meteor=18; 'reactive-off'=19 }
$sideModes = @{ off=0; solid=1; breathing=2; neon=3; wave=4; snake=5 }
Add-Type -TypeDefinition @'
using System; using System.Runtime.InteropServices; using Microsoft.Win32.SafeHandles;
public static class Hid {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] public static extern SafeFileHandle CreateFile(string f, uint a, uint s, IntPtr sec, uint d, uint fl, IntPtr t);
  [DllImport("hid.dll", SetLastError=true)] public static extern bool HidD_SetFeature(SafeFileHandle h, byte[] b, int n);
  [DllImport("hid.dll", SetLastError=true)] public static extern bool HidD_GetFeature(SafeFileHandle h, byte[] b, int n);
}
'@
# device path from the PnP instance id of the vendor interface (MI_02), same one the official driver uses
$inst = (Get-PnpDevice -PresentOnly | Where-Object InstanceId -like 'HID\VID_3151&PID_5054&MI_02*').InstanceId
if (-not $inst) { throw 'HE75 V2 not found (plug it in via USB).' }
$bs = [string][char]92
$path = $bs + $bs + '?' + $bs + $inst.Replace($bs, '#') + '#{4d1e55b2-f16f-11cf-88cb-001111000030}'
$h = [Hid]::CreateFile($path, [uint32]3221225472, 3, [IntPtr]::Zero, 3, 0, [IntPtr]::Zero)   # GENERIC_READ|WRITE, share R|W, OPEN_EXISTING
if ($h.IsInvalid) { throw "Cannot open $path (close the EPOMAKER driver app first)." }

function Send([byte[]]$cmd, [int]$ck = 8) {   # 64-byte command, checksum at byte $ck (8 for light writes, 7 for queries)
  $b = New-Object byte[] 65; for ($i=0;$i -lt $cmd.Length;$i++){ $b[$i+1] = $cmd[$i] }
  $b[$ck+1] = 255 - ((($b[1..$ck] | Measure-Object -Sum).Sum) -band 255)
  if (-not [Hid]::HidD_SetFeature($h, $b, 65)) { throw "SetFeature failed ($([Runtime.InteropServices.Marshal]::GetLastWin32Error()))" }
  $b
}
function Query([byte]$c) {
  [void](Send ([byte[]]@($c,0,0,0,0,0,0,0)) 7); Start-Sleep -Milliseconds 100
  $r = New-Object byte[] 65; if (-not [Hid]::HidD_GetFeature($h, $r, 65)) { throw 'GetFeature failed' }; $r
}
function Show($r, $side = $false) {
  $mm = if ($side) { $sideModes } else { $modes }
  $name = ($mm.GetEnumerator() | Where-Object Value -eq $r[2]).Key
  'mode={0} speed={1} brightness={2} flags={3:x2} rgb=#{4:X2}{5:X2}{6:X2}' -f $name, $(if ($side) { $r[3] } else { 4-$r[3] }), $r[4], $r[5], $r[6], $r[7], $r[8]
}
if ($Read) { $r = Query $(if ($Side) {0x88} else {0x87}); 'raw: ' + (($r[0..12] | ForEach-Object { '{0:x2}' -f $_ }) -join ' '); Show $r $Side; return }
$mm = if ($Side) { $sideModes } else { $modes }
if (-not $mm.ContainsKey($Mode)) { throw "Mode must be one of: $($mm.Keys -join ', ')" }
$rgb = [Convert]::ToInt32($Color.TrimStart('#'), 16); if ($rgb -eq 0xFFFFFF) { $rgb = 0xFAFFFA }   # firmware quirk for pure white
$flags = if ($Rainbow) { 8 } else { 7 }
$spd = if ($Side) { $Speed } else { 4-$Speed }   # side speed is not inverted
$sent = Send ([byte[]]@($(if ($Side) {8} else {7}), $mm[$Mode], $spd, $Brightness, $flags, ($rgb -shr 16), (($rgb -shr 8) -band 255), ($rgb -band 255)))
$back = Query $(if ($Side) {0x88} else {0x87})
# byte 1 is the command echo (07 vs 87), so compare from byte 2
if (($sent[2..8] -join ',') -ne ($back[2..8] -join ',')) { Write-Warning 'Readback differs from what was sent'; Show $back $Side; exit 1 }
'OK (verified by readback): ' + (Show $back $Side)
