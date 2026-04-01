# Arquivo main.py

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Aluno
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

page = 0
page_limit = 0
alunos = []
app = FastAPI(lifespan=initFunction)

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
 
def todos_alunos():
    global page, page_limit
    with Session(engine) as session:
        query = select(Aluno)
        page_limit = len(session.exec(query).all()) // 10
        return session.exec(query).all()
    
@app.get("/busca", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request):
    global page, alunos
    alunos = todos_alunos()
    return templates.TemplateResponse(request, "lista.html", 
                                      {"alunos": alunos[page*10:(page+1)*10], 
                                       "linf":page==0,
                                       "lsup":page==page_limit})
    
@app.get("/editarAlunos")
def novoAluno(request: Request):
    return templates.TemplateResponse(request, "options.html")

@app.post("/novoAluno", response_class=HTMLResponse)
def criar_aluno(nome: str = Form(...)):
    with Session(engine) as session:
        novo_aluno = Aluno(nome=nome)
        session.add(novo_aluno)
        session.commit()
        session.refresh(novo_aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {novo_aluno.nome} foi registrado(a)!</p>")
    
@app.delete("/deletaAluno", response_class=HTMLResponse)
def deletar_aluno(id: int):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if (not aluno):
            raise HTTPException(404, "Aluno não encontrado")
        session.delete(aluno)
        session.commit()
        return HTMLResponse(content=f"<p>O(a) aluno(a) {aluno.nome} foi deletado(a)!</p>")
    

# Arquivo main.py 

@app.put("/atualizaAluno", response_class=HTMLResponse)
def atualizar_aluno(id: int = Form(...), novoNome: str = Form(...)):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if (not aluno):
            raise HTTPException(404, "Aluno não encontrado")
        nomeAntigo = aluno.nome
        aluno.nome = novoNome
        session.commit()
        session.refresh(aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {nomeAntigo} foi atualizado(a) para {aluno.nome}!</p>")
    

@app.post("/anterior")
def anterior(request: Request):
    global page, alunos
    page -= 1
    page = max(0, page) 
    return templates.TemplateResponse(request, "lista.html", 
                                      {"alunos": alunos[page*10:(page+1)*10], 
                                       "linf":page==0,
                                       "lsup":page==page_limit})

@app.post("/proximo")
def proximo(request: Request):
    global page, alunos
    page += 1
    page = min(page_limit, page)
    return templates.TemplateResponse(request, "lista.html", 
                                      {"alunos": alunos[page*10:(page+1)*10], 
                                       "linf":page==0,
                                       "lsup":page==page_limit})


def buscar_alunos(busca):
    with Session(engine) as session:
        query = select(Aluno).offset(page*10).limit(10)
        
        if busca:
            query = query.where(Aluno.nome.contains(busca))
        
        query = query.order_by(Aluno.nome)
        return session.exec(query).all()
    
@app.post("/lista", response_class=HTMLResponse)
def buscar(request: Request,  busca: str | None = Form(...)):
    global page_limit, page, alunos
    print("busca é: " + busca)
    alunos = buscar_alunos(busca)
    page_limit = len(alunos) // 10
    page = 0
    return templates.TemplateResponse(request, "lista.html", 
                                      {"alunos": alunos[page*10:(page+1)*10], 
                                       "linf":page==0,
                                       "lsup":page==page_limit})