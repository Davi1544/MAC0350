# ==============================
# IMPORTS E CONFIGURAÇÃO INICIAL
# ==============================
from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response, Form
from database import create_db_and_tables
from sqlmodel import SQLModel, create_engine, Session, select
from models import Usuario, Tweet
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import logging
import time
from sqlalchemy import desc, or_, distinct
from sqlalchemy.orm import joinedload, selectinload

app = FastAPI()

# Pasta de arquivos estáticos (css, js, imagens, etc)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates HTML (organizados em pastas)
templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

# Engine do banco (inicializa depois)
engine = None

    


# ==============================
# STARTUP
# ==============================
@app.on_event("startup")
def on_startup() -> None:
    # Cria o banco e tabelas quando a API inicia
    global engine
    engine = create_db_and_tables()


# ==============================
# AUTENTICAÇÃO (DEPENDENCY)
# ==============================
def get_active_user(request: Request, session_user: Annotated[str | None, Cookie()] = None):
    with Session(engine) as session:
        # Se não tem cookie, não tem usuário logado
        if not session_user:
            return None

        # Busca usuário pelo ID do cookie
        statement = select(Usuario).where(Usuario.id == session_user)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=401, detail="Sessão inválida")

        return user
    
###
###
###
def buscar_tweets(
            session,
            handle: str | None = None, 
            tweet: int | None = None, 
            pesquisa: str | None = None):

        # Carrega os tweets com seus usuários
        query = select(Tweet).options(selectinload(Tweet.user))  # Carrega o usuário (não os filhos)

        # Se tiver código de um tweet, ele fica em destaque
        if tweet:
            query = query.where(Tweet.id == tweet)

        # Se pesquisa for fornecida, adiciona filtro para conteúdo do tweet e nome do usuário
        if pesquisa:
            query = query.where(
                or_(
                    Tweet.content.ilike(f"%{pesquisa}%"),  # Pesquisa no conteúdo do tweet
                    Tweet.user.has(Usuario.username.ilike(f"%{pesquisa}%")),  # Pesquisa no nome do usuário
                    Tweet.user.has(Usuario.handle.ilike(f"%{pesquisa}%"))  # Pesquisa no nome do usuário
                )
            )

        # Se o handle for especificado
        if handle:
            query = query.where(Tweet.user.has(handle=handle))

        if not(handle) and not(pesquisa) and not(tweet):
            query = query.where(Tweet.parent_id == None)

        query = query.order_by(desc(Tweet.post_date))
        posts = session.exec(query).all()

        # Após carregar os tweets, vamos carregar os filhos (responses)
        for post in posts:
            post.children = session.exec(select(Tweet).where(Tweet.parent_id == post.id)).all()

        return posts

@app.get("/lista_tweets")
def lista_tweets(request: Request,
                handle: str | None = None, 
                tweet: int | None = None, 
                pesquisa: str | None = None,
                user: Usuario = Depends(get_active_user)):

    with Session(engine) as session:
        return templates.TemplateResponse(
        name="lista_tweets.html",
        context={
            "request":request,
            "posts": buscar_tweets(session, 
                                   handle,
                                   tweet,
                                   pesquisa),
            "user": user
        }
    )



# ==============================
# HOME
# ==============================
@app.get("/")
def page_home(request: Request, 
              handle: str | None = None, 
              tweet: int | None = None, 
              user: Usuario = Depends(get_active_user)):
        
    with Session(engine) as session:

        # Se o handle for especificado
        perfil = None
        if handle:
            perfil = session.exec(select(Usuario).where(Usuario.handle == handle)).first()

        # Renderiza a página inicial com os posts
        return templates.TemplateResponse(
            name="home.html",
            context={
                "request": request,
                "user": user,
                "perfil": perfil,
                "tweet": tweet,
                "handle": handle
            }
        )









# ==============================
# USUÁRIOS (SIGNUP / LOGIN / LOGOUT / UPDATE)
# ==============================

# Página de cadastro
@app.get("/signup")
def page_signup(request: Request):
    return templates.TemplateResponse(
        name="signup.html",
        context={"request": request}
    )


# Criação de usuário
@app.post("/signup")
def signup(request: Request, user: Usuario):
    with Session(engine) as session:
        try:
            session.add(user)       # adiciona no banco
            session.commit()        # salva
            session.refresh(user)   # atualiza objeto

            # Redirect to home after signup
            # tell frontend to redirect
            return JSONResponse({"redirect": "/"})
        
        except Exception as e:
            print(e)
            raise


# Página de login
@app.get("/login")
def page_login(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        context={"request": request}
    )


# Login do usuário
@app.post("/login")
def login(request: Request, response: Response, user_data: dict):
    with Session(engine) as session:

        # Tenta logar com email
        statement = select(Usuario).where(Usuario.email == user_data["entry"])
        user = session.exec(statement).first()

        # Se não achou, tenta com handle
        if not user:
            statement = select(Usuario).where(Usuario.handle == user_data["entry"])
            user = session.exec(statement).first()

            if not user:
                raise HTTPException(status_code=401, detail="Invalid username or password")

        # Verifica senha
        if user.password != user_data["password"]:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Create JSONResponse and set cookie on it
        resp = JSONResponse({"redirect": "/"})
        resp.set_cookie(key="session_user", value=str(user.id), httponly=True, path="/")

        return resp


# LOGOUT
@app.post("/logout")
def logout(response: Response, request: Request):
    #response = RedirectResponse(url="/")
    response.delete_cookie("session_user")
    response.headers["HX-Trigger"] = "logout-success"
    return ""
    #return response


# profile
@app.get("/perfil")
def profile(request: Request, 
            handle : str | None = None, 
            user: Usuario = Depends(get_active_user)):

    with Session(engine) as session:
        statement = select(Usuario).where(Usuario.handle == handle)
        perfil = session.exec(statement).first()
        
        return templates.TemplateResponse(
                    name="perfil.html",
                    context={"request": request,
                            "perfil": perfil,
                            "user": user}
                )

# update_username
@app.put("/update_username")
def update_username(
    request: Request,
    username: str = Form(...),
    user: Usuario = Depends(get_active_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    with Session(engine) as session:
        db_user = session.exec(
            select(Usuario).where(Usuario.id == user.id)
        ).first()

        db_user.username = username

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        print(db_user)

        return templates.TemplateResponse(
            name="home.html",
            context={
                "request": request,
                "user": db_user,
                "perfil": db_user,
                "tweet": None,
                "handle": db_user.handle
            }
        )













# ==============================
# TWEETS
# ==============================

# Página para criar tweet
@app.get("/tweetar")
def page_post(request: Request, resposta_id: int | None = None, user: Usuario = Depends(get_active_user)):
    # Se não estiver logado, manda pro login
    if not user:
        # If request came from htmx
        if request.headers.get("HX-Request"):
            response = Response()
            response.headers["HX-Redirect"] = "/login"
            return response
        else:
            return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        request=request,
        name="tweet-form.html",
        context={"user": user, "resposta_id": resposta_id}
    )


# Criar tweet
@app.post("/post")
def post(request: Request, 
        texto: str = Form(...), 
        resposta_id: int = Form(0),
        user: Usuario = Depends(get_active_user)):
    with Session(engine) as session:
        tweet = Tweet(content=texto)

        tweet.user = user  # associa tweet ao usuário logado

        # Se for um tweet resposta
        if (resposta_id and resposta_id != 0):

            # Busca tweet pelo id da resposta
            statement = select(Tweet).where(Tweet.id == resposta_id)
            tweet_pai = session.exec(statement).first()

            # Relaciona tweet pai e tweets filhos
            if(tweet_pai != None):
                tweet.parent = tweet_pai

            try:
                session.add(tweet)
                session.commit()
                session.refresh(tweet)
                return templates.TemplateResponse(
                    request=request,
                    name="tweet_render.html",
                    context={"user": user, "post": tweet_pai}
                )
            except Exception as e:
                print(e)
                raise

        try:
            session.add(tweet)
            session.commit()
            session.refresh(tweet)
            return templates.TemplateResponse(
                name="lista_tweets.html",
                context={
                    "request":request,
                    "posts": buscar_tweets(session),
                    "user": user
                }
            )
        
        except Exception as e:
            print(e)
            raise

# deletar tweet
@app.delete("/deletar_tweet/{tweet_id}")
def deletar_tweet(tweet_id: int, response: Response, user: Usuario = Depends(get_active_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    # Buscar o tweet pelo ID
    with Session(engine) as session:
        tweet = session.exec(select(Tweet).where(Tweet.id == tweet_id)).first()

        # Verifica se o tweet existe
        if not tweet:
            raise HTTPException(status_code=404, detail="Tweet não encontrado")

        # Verifica se o usuário logado é o dono do tweet
        if tweet.user_id != user.id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este tweet")

        # Deleta o tweet
        session.delete(tweet)
        session.commit()

        return RedirectResponse(url="/lista_tweets", status_code=303)  # Redireciona para a página inicial após deletar









# ==============================
# PARTIALS (COMPONENTES HTML)
# ==============================
@app.get("/nav")
def nav(request: Request, 
        user: Usuario = Depends(get_active_user)):
    # Retorna só o navbar (provavelmente usado via include)
    return templates.TemplateResponse(
        request=request,
        name="nav.html",
        context={"user":user}
    )








# ==============================
# ROTAS AUXILIARES (DEBUG)
# ==============================

# Lista usuários (remover depois)
@app.get("/userlist")
def user_list():
    with Session(engine) as session:
        return session.exec(select(Usuario)).all()


# Lista tweets (remover depois)
@app.get("/postlist")
def post_list():
    with Session(engine) as session:
        return session.exec(select(Tweet)).all()







# ==============================
# MIDDLEWARE (LOG + TEMPO)
# ==============================

# Configuração básica de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Marca tempo antes da requisição
    start_time = time.perf_counter()

    # Executa a rota
    response = await call_next(request)

    # Calcula tempo total
    process_time = time.perf_counter() - start_time

    # Adiciona no header da resposta
    response.headers["X-Process-Time"] = str(process_time)

    # Log no terminal
    logger.info(f"Rota: {request.url.path} | Tempo: {process_time:.4f}s")

    return response