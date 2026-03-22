from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class Matricula(SQLModel, table=True):
    aluno_id: Optional[int] = Field(
        default=None,
        foreign_key="aluno.id",
        primary_key=True,
    )
    curso_id: Optional[int] = Field(
        default=None,
        foreign_key="curso.id",
        primary_key=True,
    )

class Aluno(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    nome: str
    email: str = Field(index=True, unique=True)

    cursos: List["Curso"] = Relationship(
        back_populates="alunos",
        link_model=Matricula,
    )
    
class Curso(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    nome: str
    codigo: str = Field(index=True, unique=True)
    descricao: Optional[str] = None

    alunos: List["Aluno"] = Relationship(
        back_populates="cursos",
        link_model=Matricula,
    )

class Estado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    nome: str