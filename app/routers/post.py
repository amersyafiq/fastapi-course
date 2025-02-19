from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, utils, oauth2
from ..database import get_db
from typing import Optional, List

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", response_model=List[schemas.PostOut]) #READ POSTS
def get_posts(db: Session = Depends(get_db), 
              current_user: int = Depends(oauth2.get_current_user),
              Limit: int = 10, #query parameter, eg: /login?Limit=4
              skip: int = 0,
              search: Optional[str] = ""):
    # SQL:
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    # SQLALCHEMY ORM:
    # query(models.Post): SELECT * FROM Posts
    # WHERE title = {search}
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(Limit).offset(skip).all()

    #SQL = SELECT a.*, count(b.post_id) FROM posts a LEFT (OUTER) JOIN vote b ON a.id == b.post_id GROUP BY a.id 
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
                       models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                       models.Post.id).filter(models.Post.title.contains(search)).limit(Limit).offset(skip).all()
    return results

# @router.post("/createposts")
# def create_posts(payLoad: dict = Body(...)): -- doesnt use schema
#     print(payLoad) #payLoad can be anything
#     return {"new_post": f"title {payLoad['title']} content: {payLoad['content']}"}
# # title str, content str (schema)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post) #CREATE POSTS
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # SQL:
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published)) #ONLY ACCEPT TUPLES (a,b,c)
    # new_post = cursor.fetchone()
    # conn.commit()
    
    # ORM:
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(owner_id=current_user.id, **post.dict()) #automatically unpack the dictionary
    db.add(new_post) 
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut) #GET 1 POST
def get_post(id: int, response: Response, db: Session = Depends(get_db)): #validate it as int
    # SQL:
    # cursor.execute(""" SELECT * FROM posts WHERE ID = %s """,(id,)) #SINGLE TUPLE HAVE TRAILING COMMA
    # post = cursor.fetchone()

    # ORM:
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
                       models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                       models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): #DELETE POST
    # SQL:
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    # ORM:
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): #UPDATE POST
    # SQL:
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
    #                (post.title, post.content, post.published, id))
    # index = cursor.fetchone()
    # conn.commit()
    
    # ORM:
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()