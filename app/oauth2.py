from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# JWT TOKEN CONSIST OF:
# SECRET_KEY
# ALGORITHM
# EXPIRATION TIME

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict): #data that we want to store in the payload, eg: user id (1,2,3)
    to_encode = data.copy() #make a copy of the data to encode

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #add 30 minutes to the current time for the time it expired
    to_encode.update({"exp": expire}) #include the expiration time along with the data

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) #create a token by passing the payload, algorithm & secret key

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):

    try:

        payLoad = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #when we decode, we get the payLoad data (dictionary)
        idx: str = payLoad.get("user_id") #get the user_id from payLoad and store it into id (as string)

        if idx is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=idx) #assign id to token_data, uses schemas to validate it follows str type

    except JWTError:
        raise credentials_exception
    
    return token_data
    

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    
    token_id = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_id.id).first()

    return user

#everytime user need to use protected endpoint (like creating posts) where user must be login to do,
#add a dependency in its path operation "get_current_user: int = Depends(oauth2.get_current_user)"
#that will first run get_current_user and subsequently verify_access_token that ultimately return a user id (if it matches)

