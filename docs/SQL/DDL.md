<center>

# Criação das Tabelas

</center>

---

````sql
BEGIN;

CREATE DOMAIN CodigoDisciplina AS CHAR(7) CHECK (VALUE ~ '^[A-Z]{3}[0-9]{4}$');
CREATE TYPE TipoModalidade AS ENUM('presencial', 'distancia', 'outra');

CREATE TABLE unidade_responsavel (
    id SERIAL NOT NULL,
    unidade TEXT NOT NULL,
    cidade CHAR(15) NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX unidadex_unidade ON unidade_responsavel(unidade);


CREATE TABLE disciplina (
    codigo CodigoDisciplina NOT NULL,
    modalidade TipoModalidade NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT NULL,
    matriculavel_online BOOLEAN NULL,
    horario_flexivel_turma BOOLEAN NULL,
    horario_flexivel_docente BOOLEAN NULL,
    obrigatoria_nota_final BOOLEAN NULL,
    criar_sem_solicitacao BOOLEAN NULL,
    necessita_orientador BOOLEAN NULL,
    possui_subturmas BOOLEAN NULL,
    exige_horario BOOLEAN NULL,
    multiplas_aprovacoes BOOLEAN NULL,
    qntd_avalicacoes SMALLINT NULL,
    teorica_presencial SMALLINT NOT NULL,
    pratica_presencial SMALLINT NOT NULL,
    extensionista_presencial SMALLINT NOT NULL,
    teorica_distancia SMALLINT NOT NULL,
    pratica_distancia SMALLINT NOT NULL,
    extensionista_distancia SMALLINT NOT NULL,
    carga_presencial SMALLINT NOT NULL,
    carga_distancia SMALLINT NOT NULL,
    unidade INTEGER NOT NULL,
    PRIMARY KEY (codigo),
    FOREIGN KEY (unidade) REFERENCES unidade_responsavel(id)
);

CREATE INDEX unidadex_disciplina ON disciplina(unidade);

CREATE TABLE professor (
    id SERIAL NOT NULL,
    nome TEXT UNIQUE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX nomex_professor ON professor(nome);

CREATE TABLE professor_oferta (
    professor INTEGER NOT NULL,
    disciplina_ofertada INTEGER NOT NULL,
    PRIMARY KEY (professor, disciplina_ofertada)
);

CREATE TABLE lugar (
    id SERIAL NOT NULL,
    nome TEXT UNIQUE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX nomex_lugar ON lugar(nome);

CREATE TABLE disciplina_ofertada(
    id SERIAL NOT NULL,
    codigo CodigoDisciplina NOT NULL,
    periodo NUMERIC(5, 1) NOT NULL,
    turma CHAR(5) NOT NULL,
    horario CHAR(30) NOT NULL,
    complemento_horario CHAR(30) NULL,
    vagas_total SMALLINT NOT NULL,
    vagas_ocupadas SMALLINT NOT NULL CHECK (vagas_ocupadas <= vagas_total),
    lugar INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (lugar) REFERENCES lugar(id),
	CONSTRAINT unique_codigox_oferta UNIQUE (codigo, periodo, turma)
);

CREATE INDEX codigox_oferta ON disciplina_ofertada(codigo, periodo, turma);

CREATE TABLE requisitos (
    codigo CodigoDisciplina NOT NULL,
    prerequisito TEXT NULL,
    coequivalencia TEXT NULL,
    equivalencia TEXT NULL,
    PRIMARY KEY (codigo),
    FOREIGN KEY (codigo) REFERENCES disciplina(codigo)
);

CREATE TABLE equivalencia (
    disciplina_original CodigoDisciplina NOT NULL,
    disciplina_equivalente CodigoDisciplina NOT NULL,
    PRIMARY KEY (disciplina_original, disciplina_equivalente),
    FOREIGN KEY (disciplina_original) REFERENCES disciplina(codigo),
    FOREIGN KEY (disciplina_equivalente) REFERENCES disciplina(codigo)
);

CREATE TABLE prerequisito (
    disciplina_original CodigoDisciplina NOT NULL,
    disciplina_requisito CodigoDisciplina NOT NULL,
    PRIMARY KEY (disciplina_original, disciplina_requisito),
    FOREIGN KEY (disciplina_original) REFERENCES disciplina(codigo),
    FOREIGN KEY (disciplina_requisito) REFERENCES disciplina(codigo)
);

CREATE TABLE coequivalencia (
    disciplina_original CodigoDisciplina NOT NULL,
    disciplina_coequivalente CodigoDisciplina NOT NULL,
    PRIMARY KEY (disciplina_original, disciplina_coequivalente),
    FOREIGN KEY (disciplina_original) REFERENCES disciplina(codigo),
    FOREIGN KEY (disciplina_coequivalente) REFERENCES disciplina(codigo)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO kd_user;

COMMIT;
````
