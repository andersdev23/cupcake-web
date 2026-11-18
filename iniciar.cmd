@echo off
cd /d "%~dp0"
echo Sweet Bloom - Projeto Integrador II
echo Loja: http://127.0.0.1:8010/
echo Painel: http://127.0.0.1:8010/admin.html
echo Senha: arquivo data\admin-password.txt
echo Mantenha esta janela aberta. Ctrl+C encerra o servidor.
if exist "%LocalAppData%\Programs\Python\Python314\python.exe" (
  "%LocalAppData%\Programs\Python\Python314\python.exe" app.py
) else (
  python app.py
)
if errorlevel 1 (
  echo Consulte o README. Python 3.10 ou superior precisa estar instalado.
  pause
)
