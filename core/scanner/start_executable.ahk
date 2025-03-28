#Requires Autohotkey v2.0

SetWorkingDir(A_ScriptDir)  ; Ensures a consistent starting directory.
#SingleInstance Force ;Only launch one instance of this script.
Persistent ;Will keep it running

; Set the default mouse speed to 0
; This will make the mouse move instantly to its destination
; without any acceleration or deceleration
SetDefaultMouseSpeed 0

; NOTE: Modifier Keys and Their AutoHotkey Symbol.
/*
Alt key is !
Windows key is #
Shift key is +
Control key is ^
*/

wifi_scanner := A_ScriptDir . "/WiFi-Scanner.exe"

Run(wifi_scanner)

ExitApp()
