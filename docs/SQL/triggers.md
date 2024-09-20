<center>

# Triggers e Stored Procedure

</center>

---

````sql
BEGIN;

CREATE FUNCTION inserir_oferta(
    _codigo CodigoDisciplina,
    _periodo NUMERIC(5, 1),
    _turma CHAR(3),
    _nome TEXT,
    _horario CodigoHorario[],
    _complemento_horario CHAR(30),
    _vagas_total SMALLINT,
    _vagas_ocupadas SMALLINT,
    _nome_lugar TEXT,
    _professores TEXT[]
)
RETURNS VOID AS $$
DECLARE
    id_prof INTEGER;
    id_oferta INTEGER;
    id_lugar INTEGER;
    id_horario INTEGER;
    prof TEXT;
    hor codigohorario;
BEGIN

    SELECT id INTO id_lugar
    FROM lugar
    WHERE nome = _nome_lugar;

    IF NOT FOUND THEN
        INSERT INTO lugar (nome)
        VALUES (_nome_lugar)
        RETURNING id INTO id_lugar;
    END IF;

    INSERT INTO disciplina_ofertada (codigo, periodo, turma, nome, complemento_horario,vagas_total, vagas_ocupadas, lugar)
    VALUES (_codigo, _periodo, _turma, _nome, _complemento_horario,_vagas_total, _vagas_ocupadas, id_lugar)
    RETURNING id INTO id_oferta;

    FOREACH prof IN ARRAY _professores
    LOOP
        SELECT id INTO id_prof
        FROM professor
        WHERE nome = prof;

        IF NOT FOUND THEN
            INSERT INTO professor (nome)
            VALUES (prof)
            RETURNING id INTO id_prof;
        END IF;

        INSERT INTO professor_oferta (professor, disciplina_ofertada)
        VALUES (id_prof, id_oferta);
    END LOOP;

    FOREACH hor IN ARRAY _horario
    LOOP
        SELECT id INTO id_horario
        FROM horario
        WHERE codigo = hor;

        IF FOUND THEN
            INSERT INTO disciplina_horario (horario, disciplina_ofertada)
        VALUES (id_horario, id_oferta);
        END IF;

    END LOOP;

END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
   
   
   
CREATE FUNCTION inserir_unidade(
    _unidade TEXT,
    _cidade CHAR(15)
)
RETURNS INTEGER AS $$
DECLARE
    id_unidade INTEGER;
BEGIN
    SELECT id INTO id_unidade 
    FROM unidade_responsavel 
    WHERE unidade = _unidade;

    IF NOT FOUND THEN
        INSERT INTO unidade_responsavel (unidade, cidade)
        VALUES (_unidade, _cidade)
        RETURNING id INTO id_unidade;
    END IF;

    RETURN id_unidade;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

   
   
CREATE FUNCTION popula_turmas()
RETURNS VOID AS $$
DECLARE
    i INT;
    j INT;
    resultado CodigoHorario;
BEGIN
    FOR i IN 1..5 LOOP
        FOR j IN 2..7 LOOP
			resultado := j || 'M' || i;
			INSERT INTO horario (codigo)
			VALUES (resultado);
        END LOOP;
    END LOOP;

    FOR i IN 1..7 LOOP
        FOR j IN 2..7 LOOP
			resultado := j || 'T' || i;
			INSERT INTO horario (codigo)
			VALUES (resultado);
        END LOOP;
    END LOOP;

    FOR i IN 1..4 LOOP
        FOR j IN 2..7 LOOP
			resultado := j || 'N' || i;
			INSERT INTO horario (codigo)
			VALUES (resultado);
        END LOOP;
    END LOOP;
	
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;

````