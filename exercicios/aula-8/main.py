# Arquivo main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

@app.get("/home",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "/home  /pagina1"})

@app.get("/home/pagina1", response_class=HTMLResponse)
async def pag1(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/home/pagina1"})
    return templates.TemplateResponse(request, "Pagina1.html")

@app.get("/home/pagina2", response_class=HTMLResponse)
async def pag2(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/home/pagina2"})
    return templates.TemplateResponse(request, "Pagina2.html")



# Exercício

curtidas = 0
@app.get("/exercicio",response_class=HTMLResponse)
async def root(request: Request):
    global curtidas 
    return templates.TemplateResponse(request, "e1.html", {"curtidas": curtidas})

@app.get("/curtir",response_class=HTMLResponse)
async def curtir(request: Request):
    global curtidas 
    curtidas += 1
    return templates.TemplateResponse(request, "curtidas.html", {"curtidas": curtidas})

@app.get("/zerar",response_class=HTMLResponse)
async def zerar(request: Request):
    global curtidas 
    curtidas = 0
    return templates.TemplateResponse(request, "curtidas.html", {"curtidas": curtidas})

@app.get("/tentar",response_class=HTMLResponse)
async def tentar(request: Request):
    global curtidas 
    curtidas = 0
    return templates.TemplateResponse(request, "../../pagina-professor-melhorada/index.html", {"curtidas": curtidas})