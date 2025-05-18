#!/bin/bash

# 配置
API_URL="http://8.147.108.7:8008/api/doc"
TEST_FILE="./测试数据/README.AI产品说明书.docx"

echo "1. 测试上传接口"
curl -F "file=@$TEST_FILE" "$API_URL/upload"
echo -e "\n"

echo "2. 测试文档列表接口"
curl "$API_URL/list"
echo -e "\n"

echo "3. 测试处理接口"
# 获取第一个文档名
doc_name=$(curl -s "$API_URL/list" | grep -o '"[^"\ ]\+\.docx"' | head -n1 | tr -d '"')
echo "处理文档: $doc_name"
curl -X POST "$API_URL/process/$doc_name"
echo -e "\n"

echo "4. 测试检索接口"
curl -X POST "$API_URL/query" -H "Content-Type: application/json" -d '{"prompt": "3000元以内的手机", "db_name": "百炼手机"}'
curl -X POST "$API_URL/query" -H "Content-Type: application/json" -d '{"prompt": "怎么用", "db_name": "README.AI产品说明书"}'
echo -e "\n"

echo "5. 测试删除接口"
echo "删除文档: $doc_name"
curl -X DELETE "$API_URL/delete/$doc_name"
echo -e "\n"

# 清理
echo "6. 清理测试文件"
rm -f $TEST_FILE

echo "全部测试完成。"
