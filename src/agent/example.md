Okay, I will create the new "accounting-agent" project as requested. Here is the plan:

1.  **Project Setup**: Create a new directory `accounting-agent` inside `/home/nnikolovskii/sandbox`. I will initialize it as a Poetry project.
2.  **Copy Docker Configuration**: I'll copy the `docker-compose.yml` from the `dina` project to set up the same MongoDB environment. I will remove the `backend` service as it's specific to the `dina` project's build context.
3.  **Copy Core Logic**: I will replicate the API, authorization, and database interaction logic from the `dina` project. This includes:
    *   The FastAPI application setup (`main.py`).
    *   The dependency injection container (`container.py`).
    *   The MongoDB connection logic (`mongo_db.py`, `singletons.py`).
    *   The authentication routes and services (`auth.py`, `user.py`, `password.py`).
    *   The user model (`user.py`).
4.  **Implement Test Route**: I will create a new data model `TestModel` and a new API route `/test` that is protected by authentication. This route will allow us to verify that the authentication and database logic are working correctly.
5.  **Environment Setup**: I'll create a `.env` file with the necessary environment variables for the application to run.

Here are the commands to execute these steps:

```bash
# 1. Create project directory and initialize poetry
mkdir /home/nnikolovskii/sandbox/accounting-agent
cd /home/nnikolovskii/sandbox/accounting-agent

# 2. Create the pyproject.toml file for poetry
lswrite pyproject.toml << 'EOF'
[tool.poetry]
name = "accounting-agent"
version = "0.1.0"
description = "Accounting Agent Project"
authors = ["Nikola Nikolovski <nikolovski.nikola42@gmail.com>"]
readme = "README.md"
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = {extras = ["standard"], version = "^0.115.5"}
motor = "^3.6.0"
uvicorn = "^0.30.1"
python-dotenv = "^1.0.1"
pyjwt = "^2.10.1"
cryptography = "^44.0.0"
bcrypt = "^4.2.1"
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
dependency-injector = "^4.45.0"
pydantic = "^2.9.0"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# 3. Create the same docker-compose for the database, removing the dina-specific backend service
lswrite docker-compose.yml << 'EOF'
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: mongodb1
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: example

  mongo-express:
    image: mongo-express:latest
    container_name: mongo-express1
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: root
      ME_CONFIG_MONGODB_ADMINPASSWORD: example
      ME_CONFIG_MONGODB_SERVER: mongodb

  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant1
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  mongo_data:
  qdrant_data:
EOF

# 4. Create the .env file with required secrets
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
lswrite .env << EOF
MONGO_URL=mongodb
JWT_SECRET=super-secret-key-for-jwt-that-is-secure
ALGORITHM=HS256
ENCRYPTION_KEY=${ENCRYPTION_KEY}
EOF

# 5. Create the application directory structure
mkdir -p app/api/routes app/auth/models app/auth/services app/databases app/models

# 6. Create __init__.py files to make directories importable as packages
touch app/__init__.py
touch app/api/__init__.py
touch app/api/routes/__init__.py
touch app/auth/__init__.py
touch app/auth/models/__init__.py
touch app/auth/services/__init__.py
touch app/databases/__init__.py
touch app/models/__init__.py

# 7. Copy MongoDB database logic, removing unused imports
lswrite app/databases/mongo_db.py << 'EOF'
import logging
import os
from copy import deepcopy

from bson import ObjectId
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Any, List, Dict, TypeVar, Set, AsyncGenerator, Tuple, Union
from typing import Type as TypingType
from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError, ConnectionFailure


class MongoEntry(BaseModel):
    id: Optional[str] = None


T = TypeVar('T', bound=MongoEntry)


class MongoDBDatabase:
    client: AsyncIOMotorClient

    def __init__(self, database_name: str = "library_explore", url: Optional[str] = None):
        load_dotenv()
        url = os.getenv("MONGO_URL") if url is None else url
        print(url)
        self.client = AsyncIOMotorClient(f"mongodb://root:example@{url}:27017/")
        self.db = self.client[database_name]

    async def ping(self) -> bool:
        try:
            await self.client.admin.command("ping")
            return True
        except ConnectionFailure as e:
            raise ConnectionFailure(f"Could not connect to MongoDB: {e}")

    async def add_entry(
            self,
            entity: T,
            collection_name: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        collection_name = entity.__class__.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]
        entry = entity.model_dump()
        if "id" in entry:
            entry.pop("id")
        if metadata:
            entry.update(metadata)

        result = await collection.insert_one(entry)
        return str(result.inserted_id)

    async def get_entry_from_col_values(
            self,
            columns: Dict[str, Any],
            class_type: TypingType[T],
            collection_name: Optional[str] = None,
    ) -> Optional[T]:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        query = columns

        document = await collection.find_one(query)

        if document:
            attr_dict = {key: value for key, value in document.items()}
            attr_dict["id"] = str(document["_id"])

            instance = class_type(**attr_dict)
            return instance

        return None
EOF

# 8. Create MongoDB singleton provider, removing qdrant logic
lswrite app/databases/singletons.py << 'EOF'
from typing import Optional

from app.databases.mongo_db import MongoDBDatabase

mdb = None

async def get_mongo_db(url: Optional[str] = None) -> MongoDBDatabase:
    global mdb
    if mdb is None:
        mdb = MongoDBDatabase(database_name="accounting_agent_db", url=url)
    return mdb
EOF

# 9. Create simplified User model for authentication
lswrite app/auth/models/user.py << 'EOF'
from typing import Optional
from pydantic import EmailStr
from app.databases.mongo_db import MongoEntry

class User(MongoEntry):
    email: EmailStr
    hashed_password: str
    is_google_auth: bool = False
    full_name: str
EOF

# 10. Create PasswordService for hashing and verification
lswrite app/auth/services/password.py << 'EOF'
from passlib.context import CryptContext
from app.databases.mongo_db import MongoDBDatabase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordService:
    mdb: MongoDBDatabase

    def __init__(self, mdb: MongoDBDatabase):
        self.mdb = mdb

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)
EOF

# 11. Copy UserService logic
lswrite app/auth/services/user.py << 'EOF'
from cryptography.fernet import Fernet
from pydantic import EmailStr

from app.auth.models.user import User
from app.databases.mongo_db import MongoDBDatabase


class UserService:
    mdb: MongoDBDatabase
    fernet: Fernet

    def __init__(self, mdb: MongoDBDatabase, fernet: Fernet):
        self.fernet = fernet
        self.mdb = mdb

    async def check_user_exist(self, email: EmailStr) -> bool:
        existing_user = await self.mdb.get_entry_from_col_values(
            columns={"email": email},
            class_type=User
        )
        return existing_user is not None

    async def get_user(self, email: EmailStr) -> User|None:
        user = await self.mdb.get_entry_from_col_values(
            columns={"email": email},
            class_type=User
        )

        return user
EOF

# 12. Create the dependency injection container, simplified for this project
lswrite app/container.py << 'EOF'
from dependency_injector import containers, providers
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

from app.auth.services.password import PasswordService
from app.auth.services.user import UserService
from app.databases.mongo_db import MongoDBDatabase


def create_fernet():
    """Factory function to create Fernet instance with environment validation"""
    load_dotenv()
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        raise ValueError("ENCRYPTION_KEY environment variable is not set.")
    return Fernet(encryption_key.encode())


class Container(containers.DeclarativeContainer):
    mdb = providers.Singleton(MongoDBDatabase, database_name="accounting_agent_db")
    fernet = providers.Singleton(create_fernet)

    user_service = providers.Factory(
        UserService,
        mdb=mdb,
        fernet=fernet
    )
    
    password_service = providers.Factory(
        PasswordService,
        mdb=mdb,
    )

container = Container()
EOF

# 13. Copy authentication routes, removing UserInfo and Telegram logic
lswrite app/api/routes/auth.py << 'EOF'
import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Response
from fastapi.params import Depends
from pydantic import BaseModel, EmailStr
import jwt
from starlette import status
from app.auth.models.user import User
from app.container import container
from datetime import datetime, timedelta, timezone
from jwt.exceptions import PyJWTError
from fastapi import Request

router = APIRouter()
load_dotenv()
secret = os.getenv("JWT_SECRET")
algorithm = os.getenv("ALGORITHM")


class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str


@router.post("/register")
async def register(user_data: UserRegistration):
    mdb = container.mdb()
    user_service = container.user_service()
    password_service = container.password_service()
    user_exists = await user_service.check_user_exist(user_data.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=password_service.get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_google_auth=False
    )
    await mdb.add_entry(new_user)

    return {
        "status": "success",
        "message": "Registration successful",
        "data": None
    }


class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(user_data: UserLogin, response: Response):
    user_service = container.user_service()
    password_service = container.password_service()

    user = await user_service.get_user(user_data.email)
    if not user or not password_service.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    expires = datetime.now(timezone.utc) + timedelta(minutes=60 * 24)
    jwt_token = jwt.encode(
        {"sub": user.email, "exp": expires},
        secret,
        algorithm=algorithm,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {jwt_token}",
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24,
    )

    return {
        "status": "success",
        "message": "Login successful",
        "data": {"access_token": jwt_token, "token_type": "bearer"}
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        "access_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return {
        "status": "success",
        "message": "Logged out successfully",
        "data": None
    }


async def get_current_user(request: Request) -> User:
    user_service = container.user_service()
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token = token.replace("Bearer ", "").strip()
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    user = await user_service.get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/me")
async def get_protected_data(current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "message": "User data retrieved",
        "data": {
            "email": current_user.email,
            "full_name": current_user.full_name
        }
    }
EOF

# 14. Create the new test model
lswrite app/models/test_model.py << 'EOF'
from typing import Optional
from app.databases.mongo_db import MongoEntry

class TestModel(MongoEntry):
    user_id: str
    content: str
EOF

# 15. Create the new test route
lswrite app/api/routes/test.py << 'EOF'
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import logging

from app.api.routes.auth import get_current_user
from app.auth.models.user import User
from app.databases.singletons import get_mongo_db
from app.models.test_model import TestModel

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

class TestPayload(BaseModel):
    content: str

@router.post("/")
async def create_test_entry(
    payload: TestPayload,
    current_user: User = Depends(get_current_user)
):
    """
    Creates a test entry in the database.
    This route is protected and requires authentication.
    """
    mdb = await get_mongo_db()
    test_entry = TestModel(
        user_id=str(current_user.id),
        content=payload.content
    )
    entry_id = await mdb.add_entry(test_entry)
    return {"message": "Test entry created successfully", "entry_id": entry_id, "user_email": current_user.email}
EOF

# 16. Create the main application file
lswrite app/api/main.py << 'EOF'
from contextlib import asynccontextmanager
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import auth, test
from app.databases.singletons import get_mongo_db
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logging.getLogger('pymongo').setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up...")
    await get_mongo_db()
    logging.info("MongoDB connection established.")
    yield
    logging.info("Shutting down...")
    mdb = await get_mongo_db()
    mdb.client.close()
    logging.info("MongoDB connection closed.")


app = FastAPI(lifespan=lifespan, title="Accounting Agent API")

origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": exc.errors()}
    )

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Accounting Agent API"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(test.router, prefix="/test", tags=["Testing"])

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
EOF

echo "Project 'accounting-agent' created successfully in /home/nnikolovskii/sandbox."
echo "To run the project:"
echo "1. cd /home/nnikolovskii/sandbox/accounting-agent"
echo "2. docker-compose up -d"
echo "3. poetry install"
echo "4. poetry run python app/api/main.py"
echo "The API will be available at http://localhost:5000"

```