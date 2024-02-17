# 임포트
from fastapi import FastAPI,HTTPException,Form
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
import sqlite3
import hashlib

# define vals
con = sqlite3.connect("posts.db")
cur = con.cursor()
app = FastAPI()

# define function
def getDbConnection():
    """Connect the database"""
    con = sqlite3.connect("posts.db")
    con.row_factory = sqlite3.Row
    return con

def getComment(id):
    """get comment of post"""
    con = getDbConnection()
    cur = con.cursor()
    cmt = cur.execute(f"SELECT name,content FROM comment WHERE id == {id}")
    res = ""
    for i in cmt:
        res += f"<h3>{i['name']} : {i['content']}</h3>"
    return res

def makeGetPostsHtml(id, title, name, content, comment=""):
    """return html of getPost Function"""
    body = f'''
    <br>
    <div class='navbar'>
        <h1>GanZi</h1>
        <nav>
            <a href='/'>Home</a>  
            <a href='/write'>Write</a>
        </nav>
    </div>
    <hr>
    <div class='navbar'>
        <h1 id='{id}'>{title}</h1>
        <h4>id : {id}&nbsp&nbsp name : {name}</h4>
        <h3>{content}</h3>
    </div>
    <br>
    <hr>
    <br>
    <div class='navbar'>
        {comment}
    </div>
    <br>
    <hr>
    <br>
    <div class='navbar'>
        <form id="form" hx-post="/api/uploadcmt/{id}" hx-trigger="submit" hx-target="#res">
            <input type="text" name="name" id="Iname" placeholder="Please input name."><br>
            <input type="text" name="content" id="Icontent" placeholder="Please input content."><br>
            <input type="submit" value="submit">
        </form>
        <div id="res"></div>    
    </div>
    ''' + '''        <script>
        document.querySelector("#form").addEventListener("submit", function(event) {
    if (document.getElementById('Iname').value === '' || document.getElementById('Icontent').value === '') {
        event.preventDefault();
        alert('Please enter values in all input fields.');
    } else {
        window.location.reload();
    }
});

    </script>'''
    head = '''
        <script src="https://unpkg.com/htmx.org@1.9.10" integrity="sha384-D1Kt99CQMDuVetoL1lrYwg5t+9QdHe7NLX/SoJYkXDFfX37iInKRy5xLSi8nO7UC" crossorigin="anonymous"></script>
        <link href='/GanZi.png' rel='shortcut icon' type='image/x-icon'>
    <style>
        @font-face {
            font-family: 'SejonghospitalBold';
            src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2312-1@1.1/SejonghospitalBold.woff2') format('woff2');
            font-weight: 700;font-style: normal;
        }

        body{
            font-family: 'SejonghospitalBold';
        }
        a{
            text-decoration: none;color: black;
        }
        .navbar{
            padding-left: 50px;
        }
        input, textarea {
                font-family: 'SejonghospitalBold';
                width: 300px;
                margin-bottom: 3px;
                font-size: 16px;
                font-weight: 400;
                line-height: 1.5;
                color: #212529;
                background-color: #fff;
                background-clip: padding-box;
                border: 1px solid #ced4da;
                appearance: none;
                border-radius: 4px;
                transition: border-color .15s ease-in-out, box-shadow .15s ease-in-out;
            }

            input:focus, textarea:focus {
                color: #212529;
                background-color: #fff;
                border-color: #86b7fe;
                outline: 0;
                box-shadow: 0 0 0 0.25rem rgb(13 110 253 / 25%);
            }
            button {
                cursor: pointer;
                outline: 0;
                display: inline-block;
                font-weight: 400;
                line-height: 1.5;
                text-align: center;
                background-color: transparent;
                border: 1px solid transparent;
                padding: 6px 12px;
                font-size: 1rem;
                border-radius: .25rem;
                transition: color .15s ease-in-out, background-color .15s ease-in-out, border-color .15s ease-in-out, box-shadow .15s ease-in-out;
                color: #0d6efd;
                border-color: #0d6efd;
                            color: #0d6efd;
            border-color: #0d6efd;
            }

            button:hover {
                color: #fff;
                background-color: #0d6efd;
                border-color: #0d6efd;
            }
        </style>
    '''
    return head+body

# route
@app.get("/",response_class=FileResponse)
def root():
    return "html/index.html"

@app.get("/write", response_class=FileResponse)
def write():
    return "html/write.html"

@app.get("/login", response_class=FileResponse)
def login():
    return "html/login.html"

# API
@app.get("/api/post", response_class=HTMLResponse)
def posts():
    con = getDbConnection()
    cur = con.cursor()
    res = ""
    post = cur.execute("SELECT * FROM posts")
    for i in post:
        res+=f"<h3 class='post' id='{i['id']}' hx-get='./posts/{i['id']}' hx-trigger='click'><a href='./posts/{i['id']}'>{i['title']}</a></h3>"   
    return res

@app.get("/posts/{id}", response_class=HTMLResponse)
def getPost(id: int):
    con = getDbConnection()
    cur = con.cursor()
    cur.execute("SELECT * FROM posts WHERE id = :id", {"id": id})  # parameterized query를 이용해 sqli방어
    post = cur.fetchone()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")  # 포스트가 없는 경우 404 에러 처리
    cmt = getComment(post['id'])
    return makeGetPostsHtml(post['id'], post['title'], post['name'], post['content'],cmt)# 쌈@뽕한 리턴

@app.post("/api/post/write")
def upPost(name: str = Form(...), title: str = Form(...), content: str = Form(...)):
    con = getDbConnection()
    cur = con.cursor()
    cur.execute("INSERT INTO posts (name, title, content) VALUES (?, ?, ?)", (name, title, content))
    con.commit()
    return "게시물이 성공적으로 업로드되었습니다."

@app.post("/api/uploadcmt/{id}", response_class=HTMLResponse)
def upcmt(id : int, name : str = Form(...), content : str = Form(...)):
    con = getDbConnection()
    cur = con.cursor()
    cur.execute("INSERT INTO comment (id, name, content) VALUES (?, ?, ?)", (id, name, content))
    con.commit()
    return ""
