#!/bin/bash
echo '＝＝＝＝＝＝歡迎使用本機伺服器＝＝＝＝＝＝＝＝'
source venv/bin/activate  
export FLASK_ENV=development  
flask run
