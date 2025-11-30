import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, status, Path, HTTPException, Body
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import random

# ----- 데이터 모델 정의 -----
# 유저 생성 모델
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
# 유저 수정 모델
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

# 플레이리스트 생성 모델
class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None

# 트랙 목록 수정 모델
class PlaylistTrackModification(BaseModel):
    requestingUserId: int
    trackIds: List[int]

# ----- DataBase (인메모리 저장소) -----
users: Dict[int, Dict[str, Any]] = {}
playlists: Dict[int, Dict[str, Any]] = {}

# 플레이리스트에 들어갈 트랙 데이터
tracks: Dict[int,Dict[str, Any]] = {
    101: {"id": 101, "title":"Spring flower", "artist":"Artist A"},
    102: {"id": 102, "title":"Summer Vibe", "artist":"Artist B"},
    103: {"id": 103, "title":"Autumn morning", "artist":"Artist C"},
    104: {"id": 104, "title":"Winter dream", "artist":"Artist D"},
    105: {"id": 105, "title":"All weather", "artist":"Artist E"}
}

nextUserId = 1
nextPLId = 1

app = FastAPI(
    title="202312745 실습 과제2",
    description="플레이리스트 생성 간단 API"
)

# ----- 미들 웨어 -----

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"--- [Middleware LOG] Incoming Request: {request.method} {request.url.path} ---")
    try:
        response = await call_next(request)
    # 서버 내부 오류 발생 시 500 응답
    except Exception as e:
        print(f"--- [Middleware LOG] Exception caught: {e} ---")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "서버 내부 오류 발생 (500)"}
        )
    
    process_time = time.time() - start_time

    # 응답 후 로그 출력
    print(f"--- [Middleware LOG] Responded: {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.4f}s ---")

    return response

# 보안을 위해 비밀번호 필드 제외 모든 유저 데이터 반환
def safeUserData(user_dict: Dict[str, Any])->Dict[str,Any]:
    safe_data = user_dict.copy()
    if 'password' in safe_data:
        del safe_data['password']
    return safe_data

# ----- API 구현 -----
# POST - 유저 생성
@app.post("/users", tags=["Users"], status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def createUser(user_data: UserCreate):
    global nextUserId
    userId = nextUserId
    newUser = user_data.dict()
    
    newUser["id"]=userId #유저 고유 id
    newUser["created_at"] = time.time()

    users[userId]=newUser
    nextUserId += 1

    return safeUserData(newUser) # 성공 응답

# POST - 특정 유저의 플레이리스트 생성
@app.post("/users/{userId}/playlists", tags=["Playlists"], status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def createPlaylist(
    userId: int = Path(..., description="플레이리스트를 생성할 유저의 ID"),
    playlistData: PlaylistCreate = None
):
    if userId not in users:
        # 해당하는 유저가 없을 경우 404 Not Found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"유저 ID {userId}를 찾을 수 없어 플레이리스트 생성이 불가합니다."
        )
    global nextPLId
    playlistId = nextPLId
    newPL = playlistData.dict()
    newPL["id"] = playlistId
    newPL["owner_id"] = userId # key는 snake_case 유지
    newPL["tracks"] = random.sample(list(tracks.keys()), random.randint(1, 3))
    newPL["created_at"] = time.time()

    playlists[playlistId] = newPL
    nextPLId += 1

    return newPL # 성공 응답

# GET - 특정 유저의 프로필 조회
@app.get("/users/{userId}", tags=["Users"], response_model=Dict[str, Any])
async def getUserProfile(userId: int = Path(..., description="조회할 유저의 ID")):
    user = users.get(userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"유저 ID {userId}를 찾을 수 없음"
        )
    
    return safeUserData(user)

# GET - 모든 플레이리스트 목록 조회
@app.get("/playlists", tags=["Playlists"], response_model=List[Dict[str, Any]])
async def listAllPL():
    return list(playlists.values())

# PUT - 특정 유저의 정보 수정(비밀번호 수정 포함)
@app.put("/users/{userId}", tags=["Users"], response_model=Dict[str, Any])
async def updateUserProfile(userId: int, updateData: UserUpdate):
    if userId not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"유저 ID {userId}를 찾을 수 없음."
        )
    
    user = users[userId]

    updateFields = updateData.dict(exclude_none=True)
    if not updateFields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="변경할 내용이 없음."
        )
    

    user.update(updateFields)
    user["updated_at"] = time.time()

    return safeUserData(user)

# PUT - 특정 플레이리스트의 트랙 목록 수정
@app.put("/playlists/{playlistId}/tracks", tags=["Playlists"], response_model=Dict[str, Any])
async def updatePLtracks(
    playlistId: int = Path(..., description="트랙을 수정할 플레이리스트 ID"),
    updateData: PlaylistTrackModification= Body(..., description="요청한 유저의 ID와 새로운 트랙 목록"),
):
    if playlistId not in playlists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="플레이리스트 ID를 찾을 수 없음."
        )
    
    playlist = playlists[playlistId]

    # 1. 권한 없음 오류
    if playlist.get("owner_id") != updateData.requestingUserId: # playlist key는 snake_case 유지
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="플레이리스트를 수정할 권한이 없습니다."
        )
    
    # 2. 유효한 트랙 없음
    addingTrackIds = list(tracks.keys())
    for trackId in updateData.trackIds:
        if trackId not in addingTrackIds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 트랙 ID: {trackId}"
            )

    playlist["tracks"] = updateData.trackIds
    playlist["updated_at"] = time.time()

    return playlist

# DELETE - 특정 유저를 삭제
@app.delete("/users/{userId}", tags=["Users"], status_code=status.HTTP_204_NO_CONTENT)
async def deleteUser(userId: int):
    if userId not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유저를 찾을 수 없습니다."
        )
    
    del users[userId]
    playlistsToDel = [pid for pid, playlist in playlists.items() if playlist.get("owner_id") == userId]
    for pid in playlistsToDel:
        del playlists[pid]

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# DELETE - 특정 플레이리스트를 삭제
@app.delete("/playlists/{playlistId}", tags=["Playlists"], status_code=status.HTTP_204_NO_CONTENT)
async def deletePlaylist(playlistId: int):
    if playlistId not in playlists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="플레이리스트를 찾을 수 없습니다."
        )
    
    del playlists[playlistId]

    return Response(status_code=status.HTTP_204_NO_CONTENT)
