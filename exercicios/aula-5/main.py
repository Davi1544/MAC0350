from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import time
import logging
    

app = FastAPI()

# Usuários
class Usuario(BaseModel):
    nome: str
    password: str
    bio: str

class Login(BaseModel):
    nome: str
    password: str

usuarios_db : list[Usuario] = []


# Monta a pasta "static" na rota "/static"
app.mount("/static", StaticFiles(directory="static"), name="static")

# Sintaxe recomendada: diretório como primeiro argumento posicional
templates = Jinja2Templates(directory="templates")

@app.post("/users")
def criar_usuario(user: Usuario):
    usuarios_db.append(user)
    print(user)
    print(usuarios_db)
    return {"usuario": user.nome}

@app.get("/")
def open_user(request: Request):
    return templates.TemplateResponse(
        request=request, name="sign-up.html"
    )

@app.get("/login")
def open_user(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )

@app.post("/login")
def login(login : Login, response: Response):
    # Buscamos o usuário usando um laço simples
    usuario_encontrado = None
    for u in usuarios_db:
        print(u)
        if u.nome == login.nome and u.password == login.password:
            usuario_encontrado = u
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # O servidor diz ao navegador: "Guarde esse nome no cookie 'session_user'"
    response.set_cookie(key="session_user", value=usuario_encontrado.nome)
    return {"message": "Logado com sucesso"}

# 2. A Dependência: Lendo o Cookie
def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    print("SESSION USER -> " + session_user)

    # O FastAPI busca automaticamente um cookie chamado 'session_user'
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )
    
    print("SESSION USER -> " + session_user)

    user = next((u for u in usuarios_db if u.nome == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user

# 3. Rota Protegida
@app.get("/home")
def show_profile(request: Request, user: Usuario = Depends(get_active_user)):
    print(user)
    return templates.TemplateResponse(
        request=request, 
        name="perfil.html", 
        context={"user": user.nome, "bio": user.bio}
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
    




#
# MIDDLEWARE
#
# Configuração básica de log para aparecer no terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
# 1. Código executado ANTES da rota
    start_time = time.perf_counter()

    # 2. A requisição viaja até a rota e volta como resposta
    response = await call_next(request)

    # 3. Código executado DEPOIS da rota
    process_time = time.perf_counter() - start_time

    # Adicionamos um header customizado na resposta para o cliente ver
    response.headers["X-Process-Time"] = str(process_time)

    logger.info(f"Rota: {request.url.path} | Tempo: {process_time:.4f}s")

    return response