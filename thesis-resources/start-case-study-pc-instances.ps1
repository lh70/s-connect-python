# to run this either do this once:
#  Set-ExecutionPolicy Unrestricted
# or do this for the current powershell session:
#  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
$worker_script_path = "$PSScriptRoot/../scripts/run-desktop-worker.py"

invoke-expression "cmd /c start powershell -NoExit -Command {Set-Location -Path $PSScriptRoot; `$host.UI.RawUI.WindowTitle = 'Worker 8090'; python $worker_script_path;}"
invoke-expression "cmd /c start powershell -NoExit -Command {Set-Location -Path $PSScriptRoot; `$host.UI.RawUI.WindowTitle = 'Worker 8100'; python $worker_script_path 8100;}"
invoke-expression "cmd /c start powershell -NoExit -Command {Set-Location -Path $PSScriptRoot; `$host.UI.RawUI.WindowTitle = 'Worker 8101'; python $worker_script_path 8101;}"
invoke-expression "cmd /c start powershell -NoExit -Command {Set-Location -Path $PSScriptRoot; `$host.UI.RawUI.WindowTitle = 'Worker 8102'; python $worker_script_path 8102;}"
invoke-expression "cmd /c start powershell -NoExit -Command {Set-Location -Path $PSScriptRoot; `$host.UI.RawUI.WindowTitle = 'Worker 8103'; python $worker_script_path 8103;}"
invoke-expression "cmd /c start powershell -NoExit -Command {Set-Location -Path $PSScriptRoot; `$host.UI.RawUI.WindowTitle = 'Worker 8104'; python $worker_script_path 8104;}"
invoke-expression "cmd /c start powershell -NoExit -Command {Set-Location -Path $PSScriptRoot; `$host.UI.RawUI.WindowTitle = 'Worker 8105'; python $worker_script_path 8105;}"
invoke-expression "cmd /c start powershell -NoExit -Command {Set-Location -Path $PSScriptRoot; `$host.UI.RawUI.WindowTitle = 'Worker 8106'; python $worker_script_path 8106;}"
