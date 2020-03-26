#!/bin/bash
echo '＝＝＝＝＝＝歡迎使用重新啟動腳本＝＝＝＝＝＝＝＝'
echo "更新原始碼(Y/N):"
read Code
if [ $Code = 'Y' ] 
  then 
  echo '開始更新.....'
  git pull
fi

# 刪除舊行程
echo '＝＝＝＝＝＝刪除舊行程＝＝＝＝＝＝＝＝'
kill `ps aux |grep gunicorn | awk '{ print $2 }'`
echo "是否進入工程模式(Y/N):"
read Debug
if [ $Debug = 'Y' ]
  then 
  /bin/python3 /usr/local/bin/gunicorn --reload --bind=0.0.0.0:5000 wsgi:app
else
  echo '啟用多線程(Y/N):' 
  read Line
  if [ $Line = 'Y' ]
    then 
    /bin/python3 /usr/local/bin/gunicorn --reload --workers=5 --threads=2 --bind=0.0.0.0:5000 wsgi:app -D
  else
  /bin/python3 /usr/local/bin/gunicorn --reload --bind=0.0.0.0:5000 wsgi:app -D
  fi
  echo '設定完成'
fi
