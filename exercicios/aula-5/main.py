from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
    

app = FastAPI()

# Usuários
class Usuario(BaseModel):
    nome: str
    password: str
    bio: str

class Login(BaseModel):
    nome: str
    password: str

usuarios_db = []

@app.post("/usuarios")
def criar_usuario(user: Usuario):
    usuarios_db.append(user.dict())
    return {"usuario": user.nome}

@app.get("/signup")
def open_user(request: Request):
    return templates.TemplateResponse(
        request=request, name="sign-up.html"
    )

@app.get("/login")
def open_user(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )

@app.get("/loginTrial")
def login(login : Login):
    for user in usuarios_db:
        if(user.name == login.name and user.password == login.password):
            return templates.TemplateResponse(
                request=request, name="user.html", context={"user": user}
            )
    return usuarios_db


# Monta a pasta "static" na rota "/static"
app.mount("/static", StaticFiles(directory="static"), name="static")

# Sintaxe recomendada: diretório como primeiro argumento posicional
templates = Jinja2Templates(directory="templates")

@app.get("/perfil")
def ver_perfil(request: Request, logado: bool = False):
    user = {"nome": "Rodrigo", "admin": True} if logado else None
    return templates.TemplateResponse(
        request=request, name="perfil.html", context={"user": user}
    )

@app.get("/home")
def go_home(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html"
    )

@app.get("/postagens")
def listar_posts(request: Request):
    db_posts = ["FastAPI com Jinja2", "Arquitetura REST", "HATEOAS na prática"]
    return templates.TemplateResponse(
        request=request, name="blog.html", context={"posts": db_posts}
    )
    