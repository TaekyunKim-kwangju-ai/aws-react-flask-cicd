import pytest
from app import app
from moto import mock_dynamodb2
import boto3

# DynamoDB mocking 설정
@pytest.fixture(scope='function')
def dynamodb():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='diaries',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'N'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.wait_until_exists()
        yield table

@pytest.fixture
def client(dynamodb):
    # 테스트 클라이언트 생성
    with app.test_client() as client:
        yield client

# 다이어리 조회 테스트
def test_get_diaries(client):
    response = client.get('/diaries')
    assert response.status_code == 200
    assert response.json == []

# 다이어리 생성 테스트
def test_create_diary(client):
    response = client.post('/diaries', json={'title': 'Test Title', 'content': 'Test Content'})
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['title'] == 'Test Title'
    assert response.json['content'] == 'Test Content'

# 콘텐츠가 누락된 상태로 다이어리 생성 시도
def test_create_diary_missing_content(client):
    response = client.post('/diaries', json={'title': 'Test Title'})
    assert response.status_code == 400
    assert response.json['error'] == 'Title and content are required'

# 제목이 누락된 상태로 다이어리 생성 시도
def test_create_diary_missing_title(client):
    response = client.post('/diaries', json={'content': 'Test Content'})
    assert response.status_code == 400
    assert response.json['error'] == 'Title and content are required'

# 샘플 다이어리 생성
@pytest.fixture
def create_sample_diary(client):
    response = client.post('/diaries', json={'title': 'Test Title', 'content': 'Test Content'})
    return response.json['id']

# 다이어리 업데이트 성공 테스트
def test_update_diary(client, create_sample_diary):
    diary_id = create_sample_diary
    response = client.put(f'/diaries/{diary_id}', json={'title': 'Updated Title', 'content': 'Updated Content'})
    assert response.status_code == 200
    assert response.json['title'] == 'Updated Title'
    assert response.json['content'] == 'Updated Content'

# 존재하지 않는 다이어리 업데이트 시도
def test_update_diary_not_found(client):
    response = client.put('/diaries/10000', json={'title': 'Updated Title', 'content': 'Updated Content'})
    assert response.status_code == 404
    assert response.json['error'] == "Diary not found"

# 다이어리 삭제 성공 테스트
def test_delete_diary_success(client, create_sample_diary):
    diary_id = create_sample_diary
    response = client.delete(f'/diaries/{diary_id}')
    assert response.status_code == 200

# 존재하지 않는 다이어리 삭제 시도
def test_delete_diary_not_found(client):
    response = client.delete('/diaries/10000')
    assert response.status_code == 404
    assert response.json['error'] == "Diary not found"
