import os, asyncio, uuid, json
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, WebSocketException, WebSocket, status, Request, WebSocketDisconnect
from pydantic import BaseModel
import redis, argon2, jwt
import redis.asyncio as aioredis
from jwt.exceptions import InvalidTokenError
from fastapi.middleware.cors import CORSMiddleware
import pika

hasher = argon2.PasswordHasher()

r = redis.Redis(host="database")

rps = aioredis.Redis(host="pubsub")

pubsub = rps.pubsub()
sub_queue = asyncio.Queue()
unsub_queue = asyncio.Queue()

ws_conns = {}

SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = "HS256"

class User(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user: str
    token: str

def get_user(username: str):
    return r.get(username)

def create_access_token(data, expires_delta=120):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({"exp" : expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except:
        print("encode failing?")

def check_auth_token_valid(token):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return False
    except InvalidTokenError:
        return False
    hashed_pwd = get_user(username)
    if not hashed_pwd:
        print("non existent user")
        return False
    return True

def publish_message(queue, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="queue", port=5672))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=body,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )
    connection.close()

app = FastAPI()

@app.on_event("startup")
async def listener():
    await pubsub.subscribe("__keepalive__")

    async def handle_control():
        while True:
            while not sub_queue.empty():
                channel = await sub_queue.get()
                await pubsub.subscribe(channel)

            while not unsub_queue.empty():
                channel = await unsub_queue.get()
                await pubsub.unsubscribe(channel)

            await asyncio.sleep(0.05)

    async def listen_loop():
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            job_id = message["channel"].decode()
            result = message["data"].decode()

            print(f"Result for {job_id}: {result}")
            ws_connection = ws_conns[job_id]
            await ws_connection.send_text(result)
            await unsub_queue.put(job_id)
            ws_conns.pop(job_id)

    # Start both tasks in the background
    asyncio.create_task(handle_control())
    asyncio.create_task(listen_loop())

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
def login_user(user: User):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    hashed_pwd = get_user(user.username)
    if not hashed_pwd:
        raise credentials_exception
    try:
        res = hasher.verify(hashed_pwd, user.password)
        print(res)
        access_token = create_access_token(data={"sub" : user.username})
        return LoginResponse(token=access_token, user=user.username)
    except:
        raise credentials_exception

@app.post("/register")
async def register_user(user: User):
    if get_user(user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User {user.username} already exists")
    hashed_password = hasher.hash(user.password)
    r.set(user.username, hashed_password)
    return {"message" : f"User {user.username} succesfully registered"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    auth_token = websocket.headers.get("sec-websocket-protocol")
    print(auth_token)
    exception = WebSocketException(code=status.HTTP_401_UNAUTHORIZED, reason="Invalid credentials")
    if not auth_token or not check_auth_token_valid(auth_token):
        raise exception
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print("Received from client:", data)
            job_id = str(uuid.uuid4())
            ws_conns[job_id] = websocket # store websocket connections
            code_object = json.loads(data)
            code_object["job_id"] = job_id
            job_data = json.dumps(code_object)
            print("Sending to worker:", job_data)
            publish_message("task_queue", job_data)
            await sub_queue.put(job_id)
    except WebSocketDisconnect:
        print("Client disconnected")
