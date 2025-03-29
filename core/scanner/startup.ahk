#Requires Autohotkey v2.0

SetWorkingDir(A_ScriptDir)  ; Ensures a consistent starting directory.
#SingleInstance Force ;Only launch one instance of this script.
Persistent ;Will keep it running

; NOTE: Modifier Keys and Their AutoHotkey Symbol.
/*
Alt key is !
Windows key is #
Shift key is +
Control key is ^
*/

wifi_scanner := A_ScriptDir . "/wifi_scanner.py"

Run(wifi_scanner)

ExitApp()
