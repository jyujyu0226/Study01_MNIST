#!/bin/bash
# Finder에서 더블클릭하면 app.py를 실행합니다.
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 app.py
else
  echo "python3가 설치되어 있지 않습니다. https://www.python.org/downloads/ 에서 설치해 주세요."
fi
echo
read -n 1 -s -r -p "끝났습니다. 아무 키나 누르면 닫힙니다."
