from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from database import create_db_and_tables
from sqlmodel import SQLModel, create_engine, Session, select
from models import Usuario, Tweet
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import logging
import time

app = FastAPI()

# Monta a pasta "static" na rota "/static"
app.mount("/static", StaticFiles(directory="static"), name="static")

# Sintaxe recomendada: diretório como primeiro argumento posicional
templates = Jinja2Templates(directory="templates")

engine = None

@app.on_event("startup")
def on_startup() -> None:
    global engine
    engine = create_db_and_tables()

@app.get("/")
def page_home(request: Request, handle : str = None):
    with Session(engine) as session:
        query = select(Tweet)
        response = {}

        # TODO: if handle is specified, only show tweets from that user (sort by date)
        # if(nome):
        #    query = query.where(Tweet.nome == nome)
                
        response = session.exec(query).all()

        return templates.TemplateResponse(
            name="home.html", 
            context={
                "request": request,
                "posts": response
            }
        ) 
    
#
# USERs
#
@app.get("/signup")
def page_signup(request: Request):
    return templates.TemplateResponse(
            name="signup.html", 
            context={
                "request": request,
            }
        ) 

@app.post("/signup")
def signup(user: Usuario):
    with Session(engine) as session:
        print(user)
        try:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            print(e)
            raise

@app.get("/login")
def page_signup(request: Request):
    return templates.TemplateResponse(
            name="login.html", 
            context={
                "request": request,
            }
        ) 

@app.post("/login")
def login(request: Request, response: Response, user_data : dict):
    with Session(engine) as session:
        print(user_data)
        print("\n\n\n\n")
        statement = select(Usuario).where(Usuario.email == user_data["entry"])
        user = session.exec(statement).first()
        
        if not user:
            statement = select(Usuario).where(Usuario.handle == user_data["entry"])
            user = session.exec(statement).first()

            if not user:
                raise HTTPException(status_code=401, detail="Invalid username or password")
        
        if not user.password == user_data["password"]:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Criando cookie
        response.set_cookie(key="session_user", value=user.id)
        
        return {"message": "Logged in!"}

def get_active_user(request: Request, session_user: Annotated[str | None, Cookie()] = None):
    with Session(engine) as session:
        # O FastAPI busca automaticamente um cookie chamado 'session_user'
        if not session_user:
            return None

        statement = select(Usuario).where(Usuario.id == session_user)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=401, detail="Sessão inválida")
        
        return user

#
# TWEETs
#

@app.get("/tweetar")
def page_post(request: Request, user: Usuario = Depends(get_active_user)):
    if not user:
        return templates.TemplateResponse(
            request=request, name="login.html"
        )   
    
    return templates.TemplateResponse(
        request=request, name="tweet-form.html", context={"user" : user}
    )

@app.post("/post")
def post(tweet: Tweet, user: Usuario = Depends(get_active_user)):
    tweet.user = user
    with Session(engine) as session:
        print(tweet)
        try:
            session.add(tweet)
            session.commit()
            session.refresh(tweet)
            return tweet
        except Exception as e:
            print(e)
            raise

""" @app.get("/alunos")
def return_users(request: Request, nome : str = None):
    with Session(engine) as session:
        query = select(Aluno)
        response = {}
        if(nome):
            query = query.where(Aluno.nome == nome)
                
        response = session.exec(query).all()

        return templates.TemplateResponse(
            name="alunos.html", 
            context={
                "request": request,
                "alunos": response
            }
        )   
    
@app.post("/alunos")
def criar_aluno(aluno: Aluno):
    with Session(engine) as session:
        try:
            session.add(aluno)
            session.commit()
            session.refresh(aluno)
            return aluno
        except Exception as e:
            print(e)
            raise
        #{
        #    "id": aluno.id,
        #    "nome": aluno.nome,
        #    "email": aluno.email
        #}

@app.post("/cursos")
def criar_curso(curso: Curso):
    with Session(engine) as session:
        session.add(curso)
        session.commit()
        session.refresh(curso)
        return curso

@app.post("/matriculas")
def matricular(aluno_id: int, curso_id: int):
    with Session(engine) as session:
        matricula = Matricula(
            aluno_id=aluno_id,
            curso_id=curso_id
        )

        session.add(matricula)
        session.commit()

        return matricula """




#
# AUXILIARY ROUTES
#

@app.get("/userlist") # REMOVERRRR
def page_signup(request: Request):
    with Session(engine) as session:
        query = select(Usuario)
        response = {}
        response = session.exec(query).all()

        return response

@app.get("/postlist") # REMOVERRRR
def page_signup(request: Request):
    with Session(engine) as session:
        query = select(Tweet)
        response = {}
        response = session.exec(query).all()

        return response
    








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