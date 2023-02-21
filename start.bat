@echo off
if "%1"=="h" goto begin
start mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:begin

python -c "from newdao import WudaoServer; ws=WudaoServer(); ws.run()"