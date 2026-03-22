from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from database import create_db_and_tables
from sqlmodel import SQLModel, create_engine, Session, select
from velho.models import Aluno, Curso, Matricula, Estado
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
def open_user(request: Request):
    return templates.TemplateResponse(
        request=request, name="aluno-form.html"
    )

@app.get("/alunos")
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

        return matricula