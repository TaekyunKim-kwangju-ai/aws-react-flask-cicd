from flask import Flask, jsonify, request
from flask_cors import CORS
import boto3

app = Flask(__name__)
CORS(app)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('diaries')

def get_next_id():
    response = table.scan()
    if 'Items' in response and len(response['Items']) > 0:
        ids = max([item['id'] for item in response['Items']])
        return ids + 1
    return 1

next_id = get_next_id()

@app.route("/diaries", methods=['GET'])
def get_diaries():
    items = table.scan()
    return jsonify(items['Items'])

@app.route("/diaries", methods=['POST'])
def create_diary():
    global next_id
    data = request.json

    if 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content are required'}), 400
    
    diary = {
        'id': next_id,
        'title': data['title'],
        'content': data['content']
    }

    table.put_item(Item=diary)
    next_id += 1
    return jsonify(diary), 201

@app.route("/diaries/<int:diary_id>", methods=['PUT'])
def update_diary(diary_id):
    data = request.json
    diary = table.get_item(Key={'id': diary_id}).get('Item')

    # 만약에 수정할 다이어리가 없다면, Diary not Found 에러 반환, 응답코드 404
    if diary is None:
        return jsonify({'error': 'Diary not found'}), 404

    # diary 변수 업데이트
    if 'title' in data:
        diary['title'] = data['title']

    if 'content' in data:
        diary['content'] = data['content']

    # diaries 딕셔너리 전역변수 업데이트
    table.put_item(Item=diary)

    # json 형식으로 업데이트된 다이어리 반환, 응답코드 200(기본값)
    return jsonify(diary)

@app.route("/diaries/<int:diary_id>", methods=['DELETE'])
def delete_diary(diary_id):
    diary = table.get_item(Key={'id': diary_id}).get('Item')

    # 삭제할 다이어리가 없을 때, 404
    if diary is None:
        return jsonify({'error': 'Diary not found'}), 404
    
    # 다이어리 제거
    table.delete_item(Key={'id': diary_id})
    
    return jsonify(diary)