curl -X POST http://127.0.0.1:8008/query \ 
 -H "Content-Type: application/json" -d \ 
 '{"prompt": "3000元以内的手机", "db_name": "百炼手机"}';

curl -X POST http://127.0.0.1:8008/query \ 
 -H "Content-Type: application/json" -d \ 
 '{"prompt": "怎么用", "db_name": "README.AI产品说明书"}'
 