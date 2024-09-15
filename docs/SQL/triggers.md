<center>

# Triggers e Stored Procedure

</center>

---

````sql
BEGIN;

CREATE FUNCTION inserir_oferta(
    _codigo CodigoDisciplina, 
    _periodo NUMERIC(5, 1), 
    _turma SMALLINT, 
    _horario CHAR(30), 
    _complemento_horario CHAR(30), 
    _vagas_total SMALLINT, 
    _vagas_ocupadas SMALLINT, 
    _lugar INTEGER, 
    _professores TEXT[]
)
RETURNS VOID AS $$
DECLARE
    id_prof INTEGER;
    id_oferta INTEGER;
    prof TEXT;
BEGIN
    INSERT INTO disciplina_ofertada (
        codigo, periodo, turma, horario, complemento_horario, 
        vagas_total, vagas_ocupadas, lugar
    )
    VALUES (
        _codigo, _periodo, _turma, _horario, _complemento_horario, 
        _vagas_total, _vagas_ocupadas, _lugar
    )
    RETURNING id INTO id_oferta; 

    FOREACH prof IN ARRAY _professores
    LOOP
        SELECT id INTO id_prof FROM professor WHERE nome = prof;
        
        IF NOT FOUND THEN
            INSERT INTO professor (nome)
            VALUES (prof) 
            RETURNING id INTO id_prof;
        END IF;

        INSERT INTO professor_oferta (professor, disciplina_ofertada)
        VALUES (id_prof, id_oferta);
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
   
CREATE FUNCTION inserir_lugar(
    _nome TEXT
)
RETURNS INTEGER AS $$
DECLARE
    id_lugar INTEGER;
BEGIN
    SELECT id INTO id_lugar 
    FROM lugar 
    WHERE nome = _nome;

    IF NOT FOUND THEN
        INSERT INTO lugar (nome)
        VALUES (_nome)
        RETURNING id INTO id_lugar;
    END IF;

    RETURN id_lugar;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;

````