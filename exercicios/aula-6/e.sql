/*
Entregador
ID do entregador - entregador_id - (INTEGER)
Nome do entregador responsável - nome - (TEXT)
Contato do entregador responsável - contato - (TEXT)

Cliente
ID do cliente - cliente_id - (INTEGER)
Nome do cliente - nome - (TEXT)
Informações de contato do cliente - contato - (TEXT)
Endereço do cliente - endereco_id - (INTEGER)

Vendedor
ID do vendedor - vendedor_id - (INTEGER)
Nome do vendedor - nome - (TEXT)
Contato do vendedor - contato - (TEXT)

Fabricante
ID do fabricante - fabricante_id - (INTEGER)
Nome do fabricante - nome - (TEXT)

Produto
ID do produto - produto_id - (INTEGER)
Nome do produto - nome - (TEXT)
ID apontando para um fabricante - fabricante_id - (INTEGER)
->Considere que cada pedido entregará exclusivamente um produto
(Ou seja, é apenas uma FOREIGN_KEY apontando para um produto(produto_id))
*/
CREATE TABLE entregador (
    entregador_id integer PRIMARY KEY,
    nome TEXT,
    contato TEXT
);

CREATE TABLE cliente (
    cliente_id INTEGER PRIMARY KEY,
    nome TEXT,
    contato TEXT,
    endereco_id INTEGER,

    FOREIGN KEY (endereco_id) REFERENCES endereco(endereco_id)
);

CREATE TABLE endereco (
    endereco_id INTEGER PRIMARY KEY,
    rua TEXT NOT NULL,
    numero TEXT NOT NULL,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    cep TEXT NOT NULL
);

CREATE TABLE vendedor (
    vendedor_id PRIMARY KEY,
    nome TEXT,
    contato TEXT
);

CREATE TABLE fabricante (
    fabricante_id PRIMARY KEY,
    nome TEXT
);

CREATE TABLE produto (
    produto_id PRIMARY KEY,
    nome TEXT,
    fabricante_id INTEGER,

    FOREIGN KEY (fabricante_id) REFERENCES fabricante(fabricante_id)
);

CREATE TABLE pedido (
    pedido_id INTEGER PRIMARY KEY,
    
    status_entrega TEXT NOT NULL,
    
    entregador_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    vendedor_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,

    FOREIGN KEY (entregador_id) REFERENCES entregador(entregador_id),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id),
    FOREIGN KEY (vendedor_id) REFERENCES vendedor(vendedor_id),
    FOREIGN KEY (produto_id) REFERENCES produto(produto_id)
);