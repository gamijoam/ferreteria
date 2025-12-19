Set WshShell = CreateObject("WScript.Shell")
' El 0 al final significa "Esconder Ventana"
WshShell.Run chr(34) & "run_ferreteria.bat" & Chr(34), 0
Set WshShell = Nothing
