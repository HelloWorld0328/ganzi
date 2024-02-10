# 임포트
from fastapi import FastAPI,HTTPException,Form
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3

# define vals
con = sqlite3.connect("posts.db")
cur = con.cursor()
app = FastAPI()

class M_post(BaseModel):
    name : str
    title : str
    content : str

def getDatabaseConnection():
    """Connect the database"""
    con = sqlite3.connect("posts.db")
    con.row_factory = sqlite3.Row
    return con

# route
@app.get("/",response_class=FileResponse)
def root():
    return "html/index.html"

@app.get("/write", response_class=FileResponse)
def write():
    return "html/write.html"

# API
@app.get("/api/post", response_class=HTMLResponse)
def posts():
    con = getDatabaseConnection()
    cur = con.cursor()
    res = ""
    post = cur.execute("SELECT * FROM posts")
    for i in post:
        res+=f"<h3 class='post' id='{i['id']}' hx-get='./posts/{i['id']}' hx-trigger='click'><a href='./posts/{i['id']}'>{i['title']}</a></h3>"   
    return res

@app.get("/posts/{id}", response_class=HTMLResponse)
def getPost(id: int):
    con = getDatabaseConnection()
    cur = con.cursor()
    cur.execute("SELECT * FROM posts WHERE id = :id", {"id": id})  # parameterized query를 이용해 sqli방어
    post = cur.fetchone()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")  # 포스트가 없는 경우 404 에러 처리
    ret = f"<br><div class='navbar'><h1>GanZi</h1><nav><a href='/'>Home</a>  <a href='/write'>Write</a></nav></div><hr><div class='navbar'><h1 id='{post['id']}'>{post['title']}</h1><h4>id : {post['id']}&nbsp&nbsp name : {post['name']}</h4><h3>{post['content']}</h3></div>"
    return "    <link href='/GanZi.png' rel='shortcut icon' type='image/x-icon'><style>@font-face {font-family: 'SejonghospitalBold';src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2312-1@1.1/SejonghospitalBold.woff2') format('woff2');font-weight: 700;font-style: normal;}body{font-family: 'SejonghospitalBold';}a{text-decoration: none;color: black;}.navbar{padding-left: 50px;}</style>"+ret # 쌈@뽕한 리턴

@app.post("/api/post/write")
def upPost(name: str = Form(...), title: str = Form(...), content: str = Form(...)):
    con = getDatabaseConnection()
    cur = con.cursor()
    post_data = M_post(name=name, title=title, content=content)
    cur.execute("INSERT INTO posts (name, title, content) VALUES (?, ?, ?)", (name, title, content))
    con.commit()
    return "게시물이 성공적으로 업로드되었습니다."