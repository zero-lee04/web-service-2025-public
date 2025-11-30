# web-service-2025-public
# 1. 프로젝트 개요
# FastAPI 프레임워크를 사용해 음악 스트리밍 서비스의 핵심 기능인 유저 및 그 유저의 플레이리스트 관리 API를 구현한 백엔드 서버이다. POST, GET, PUT, DELETE 메서드를 사용하여 유저 생성, 조회, 수정, 삭제 그리고 그 유저의 플레이리스트 생성, 조회, 수정, 삭제 기능을 구현했다.

# 2. 주요 기능
# [1]. 유저 관리
# 메서드 | 경로 | 설명
# POST | /users | 새로운 유저 생성( 유저에 대한 고유 ID도 자동 생성)
# GET | /users/{userId} | 특정 유저의 프로필을 조회
# PUT | /users/{userId} | 특정 유저의 정보 수정(이름, 이메일, 비밀번호)
# DELETE | /users/{userId} | 유저 및 유저 소유의 플레이리스트 삭제

# [2]. 플레이리스트 관리
# POST | /users/{userId}/playlists | 특정 유저의 플레이리스트 생성(랜덤 트랙을 포함)
# GET | /playlists | 생성된 플레이리스트 목록 조회
# PUT | /playlists/{playlistId}/tracks | 특정 플레이리스트의 트랙 목록을 수정
# DELETE | /playlists/{playlistId} | 플레이리스트 삭제

# 3. 프로젝트 실행 방법
# [1]. 필수 패키지 설치: pip install fastapi[all] uvicorn
# [2]. 서버 실행 : uvicorn main:app --reload
# [3]. API 서버 테스트 : http://127.0.0.1:8000/docs
