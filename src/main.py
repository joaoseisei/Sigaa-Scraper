import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import psycopg2
import threading

logo = r"""
$$\   $$\ $$$$$$$\                                     $$$$$$\   $$$$$$\  
$$ | $$  |$$  __$$\                                   $$  __$$\ $$  __$$\ 
$$ |$$  / $$ |  $$ |$$$$$$\$$$$\   $$$$$$\  $$\   $$\ $$ /  \__|$$ /  \__|
$$$$$  /  $$ |  $$ |$$  _$$  _$$\ $$  __$$\ $$ |  $$ |\$$$$$$\  \$$$$$$\  
$$  $$<   $$ |  $$ |$$ / $$ / $$ |$$$$$$$$ |$$ |  $$ | \____$$\  \____$$\ 
$$ |\$$\  $$ |  $$ |$$ | $$ | $$ |$$   ____|$$ |  $$ |$$\   $$ |$$\   $$ |
$$ | \$$\ $$$$$$$  |$$ | $$ | $$ |\$$$$$$$\ \$$$$$$  |\$$$$$$  |\$$$$$$  |
\__|  \__|\_______/ \__| \__| \__| \_______| \______/  \______/  \______/ 
"""

with open('proxies_funcionais.txt', 'r') as f:
    proxies = f.read().split("\n")


class DatabaseConnection:
    def __init__(self):
        self.database = "KDmeuSS"
        self.user = "kd_user"
        self.password = "123"
        self.host = "localhost"
        self.port = "5432"
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print(logo)
        except Exception as error:
            print("Erro ao conectar ou consultar o banco de dados:", error)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_fetchone(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as error:
            print("Erro ao executar a consulta:", error)
            return None

    def execute_fetchall(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as error:
            print("Erro ao executar a consulta:", error)
            return None

    def execute_commit(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            print("\033[92mAlterações salvas no banco de dados.\033[0m")
        except Exception as error:
            print("\033[91mErro ao executar e salvar a consulta:\033[0m", error)
            self.connection.rollback()

db = DatabaseConnection()

class SigaaScraper:
    def __init__(self):
        self.url = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
        self.timeout = 2
        self.contador_proxies = 0
        self.unidades = []
        self.contador_unidades = 2
        self.turmas_encontradas = []
        self.contador_turmas = 0
        self.regex_turma = re.compile(
            r'^(?P<turma>\d{2})\s+'  # Captura o número da turma (2 dígitos)
            r'(?P<periodo>\d{4}\.\d)\s+'  # Captura o período no formato XXXX.X
            r'(?P<docente>(?:[A-Za-zÀ-ÿ ]+(?: [A-Za-zÀ-ÿ ]+)+ ?(?:\(\d+h\))?\n?)+)'  # Captura um ou mais docentes (inclui possível quebra de linha)
            r'\n?(?P<horario>[A-Z0-9 ]+)'  # Captura o horário no formato de letras e números (ex: 7M1234 6T2345)
            r'\s?(?P<complemento_horario>\([\d/ -]+\))?'  # Captura o complemento do horário (opcional), no formato (DD/MM/AAAA - DD/MM/AAAA)
            r'\s+(?P<vagas_total>\d+)\s+'  # Captura o número total de vagas
            r'(?P<vagas_ocupadas>\d+)\s+'  # Captura o número de vagas ocupadas
            r'(?P<local>.+)$',  # Captura o local
            re.MULTILINE
        )

    def set_unidades(self, driver):
        time.sleep(1)
        try:
            elemento = WebDriverWait(driver, self.timeout).until(
                EC.element_to_be_clickable((By.ID, 'formTurma:inputDepto'))
            )
            select = Select(elemento)
            self.unidades = [opcao.get_attribute('value') for opcao in select.options]

        except (NoSuchElementException, TimeoutException) as e:
            print(f'Erro ao localizar o dropdown: {e}')

    def escolhe_unidade(self, driver):
        try:
            elemento = WebDriverWait(driver, self.timeout).until(
                EC.element_to_be_clickable((By.ID, 'formTurma:inputDepto'))
            )
            select = Select(elemento)
            self.contador_unidades += 1
            select.select_by_value(self.unidades[self.contador_unidades])

        except (NoSuchElementException, TimeoutException) as e:
            print(f'Erro ao localizar o dropdown: {e}')

    def escolher_nivel(self, driver):
        try:
            elemento = WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, 'formTurma:inputNivel'))
            )
            elemento.send_keys('GRADUAÇÃO')
        except (NoSuchElementException, TimeoutException) as e:
            print(f'Erro ao localizar o dropdown: {e}')

    def buscar(self, driver):
        try:
            elemento = WebDriverWait(driver, self.timeout).until(
                EC.element_to_be_clickable((By.NAME, 'formTurma:j_id_jsp_1370969402_11'))
            )
            driver.execute_script("arguments[0].click();", elemento)
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Erro ao tentar clicar em buscar: {e}")

    def buscar_info_materias(self, driver):
        linhas = driver.find_elements(By.CLASS_NAME, 'agrupador')
        for linha in linhas:
            link = linha.find_element(By.TAG_NAME, 'a')
            if link:
                id_link = link.get_attribute('id')
                self.turmas_encontradas.append(id_link)

    def extrair_numero(self, texto):
        match = re.match(r"(\d+)(\D*)", texto.strip())
        if match:
            return int(match.group(1))
        return None

    def insere_disciplina(self, driver):
        for turma in self.turmas_encontradas:
            try:
                elemento = WebDriverWait(driver, self.timeout).until(
                    EC.element_to_be_clickable((By.ID, turma))
                )
                driver.execute_script("arguments[0].click();", elemento)
                WebDriverWait(driver, self.timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                curso_info = {
                    'nome': None,
                    'codigo': None,
                    'descricao': None,
                    'modalidade': None,
                    'pre_requisitos': None,
                    'coequivalencia': None,
                    'equivalencia': None,
                    'excluir_avaliacao': None,
                    'matriculavel_online': None,
                    'horario_flexivel_turma': None,
                    'horario_flexivel_docente': None,
                    'obrigatoriedade_nota_final': None,
                    'criar_turma_sem_solicitacao': None,
                    'necessita_orientador': None,
                    'possui_subturmas': None,
                    'exige_horario': None,
                    'permite_multiplas_aprovacoes': None,
                    'quantidade_avaliacoes': None,
                    'teorica_presencial': None,
                    'pratica_presencial': None,
                    'extensionista_presencial': None,
                    'carga_horaria_presencial': None,
                    'teorica_distancia': None,
                    'pratica_distancia': None,
                    'extensionista_distancia': None,
                    'carga_horaria_distancia': None,
                }
                unidade = {
                    'unidade': None,
                    'cidade': None
                }
                modalidade_mapping = {
                    'Distância': 'distancia',
                    'Presencial': 'presencial'
                }
                boolean_mapping = {
                    'Não': False,
                    'Sim': True
                }
                i = 0
                linhas = driver.find_elements(By.TAG_NAME, 'td')
                curso_info['modalidade'] = modalidade_mapping.get(linhas[1].text.strip(), 'outra')
                info = linhas[2].text.strip().split(' - ')
                unidade['unidade'] = info[0]
                unidade['cidade'] = info[1]
                curso_info['codigo'] = linhas[3].text.strip()
                curso_info['nome'] = linhas[4].text.strip()
                curso_info['pre_requisitos'] = None if linhas[5].text.strip() == '-' else linhas[5].text.strip()
                curso_info['coequivalencia'] = None if linhas[6].text.strip() == '-' else linhas[6].text.strip()
                curso_info['equivalencia'] = None if linhas[7].text.strip() == '-' else linhas[7].text.strip()
                curso_info['excluir_avaliacao'] = boolean_mapping.get(linhas[8].text.strip(), None)
                curso_info['matriculavel_online'] = boolean_mapping.get(linhas[9].text.strip(), None)
                curso_info['horario_flexivel_turma'] = boolean_mapping.get(linhas[10].text.strip(), None)
                curso_info['horario_flexivel_docente'] = boolean_mapping.get(linhas[11].text.strip(), None)
                curso_info['obrigatoriedade_nota_final'] = boolean_mapping.get(linhas[12].text.strip(), None)
                curso_info['criar_turma_sem_solicitacao'] = boolean_mapping.get(linhas[13].text.strip(), None)
                curso_info['necessita_orientador'] = boolean_mapping.get(linhas[14].text.strip(), None)
                curso_info['possui_subturmas'] = boolean_mapping.get(linhas[15].text.strip(), None)
                curso_info['exige_horario'] = boolean_mapping.get(linhas[16].text.strip(), None)
                curso_info['permite_multiplas_aprovacoes'] = boolean_mapping.get(linhas[17].text.strip(), None)
                if linhas[19].text.strip().isdigit():
                    i+=1
                curso_info['descricao'] = linhas[i+19].text.strip()
                curso_info['teorica_presencial'] = self.extrair_numero(linhas[i+23].text) or 0
                curso_info['pratica_presencial'] = self.extrair_numero(linhas[i+25].text) or 0
                curso_info['extensionista_presencial'] = self.extrair_numero(linhas[i+27].text) or 0
                curso_info['carga_horaria_presencial'] = self.extrair_numero(linhas[i+29].text) or 0
                curso_info['teorica_distancia'] = self.extrair_numero(linhas[i+31].text) or 0
                curso_info['pratica_distancia'] = self.extrair_numero(linhas[i+33].text) or 0
                curso_info['extensionista_distancia'] = self.extrair_numero(linhas[i+35].text) or 0
                curso_info['carga_horaria_distancia'] = self.extrair_numero(linhas[i+37].text) or 0
                try:
                    curso_info['quantidade_avaliacoes'] = int(linhas[i+18].text.strip())
                except ValueError:
                    curso_info['quantidade_avaliacoes'] = 0

                codigo_unidade = db.execute_fetchone("""
                    SELECT inserir_unidade(%s, %s)
                """,(unidade['unidade'], unidade['cidade'],))[0]

                db.execute_commit("""
                    INSERT INTO disciplina (
                    codigo, modalidade, nome, descricao, matriculavel_online, 
                    horario_flexivel_turma, horario_flexivel_docente, obrigatoria_nota_final, 
                    criar_sem_solicitacao, necessita_orientador, possui_subturmas, exige_horario, 
                    multiplas_aprovacoes, qntd_avalicacoes, teorica_presencial, pratica_presencial, 
                    extensionista_presencial, teorica_distancia, pratica_distancia, 
                    extensionista_distancia, carga_presencial, carga_distancia, unidade
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    curso_info['codigo'],
                    curso_info['modalidade'],
                    curso_info['nome'],
                    curso_info['descricao'],
                    curso_info['matriculavel_online'],
                    curso_info['horario_flexivel_turma'],
                    curso_info['horario_flexivel_docente'],
                    curso_info['obrigatoriedade_nota_final'],
                    curso_info['criar_turma_sem_solicitacao'],
                    curso_info['necessita_orientador'],
                    curso_info['possui_subturmas'],
                    curso_info['exige_horario'],
                    curso_info['permite_multiplas_aprovacoes'],
                    curso_info['quantidade_avaliacoes'],
                    curso_info['teorica_presencial'],
                    curso_info['pratica_presencial'],
                    curso_info['extensionista_presencial'],
                    curso_info['teorica_distancia'],
                    curso_info['pratica_distancia'],
                    curso_info['extensionista_distancia'],
                    curso_info['carga_horaria_presencial'],
                    curso_info['carga_horaria_distancia'],
                    codigo_unidade
                ))

                db.execute_commit("""
                    INSERT INTO requisitos (codigo, equivalencia, prerequisito, coequivalencia)
                    VALUES (%s, %s, %s, %s);
                """, (
                    curso_info['codigo'],
                    curso_info['pre_requisitos'],
                    curso_info['coequivalencia'],
                    curso_info['equivalencia'],
                ))
                time.sleep(2)
                driver.back()
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'agrupador'))
                )
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Erro ao tentar clicar na turma {turma}: {e}")

    def insere_oferta(self, driver):
        try:
            div_turmas = driver.find_element(By.ID, 'turmasAbertas')
            tbody = div_turmas.find_element(By.TAG_NAME, 'tbody')
            linhas_turmas = tbody.find_elements(By.TAG_NAME, 'tr')
            i = 0
            codigo = ''
            while i < len(linhas_turmas):
                linha = linhas_turmas[i]
                if 'agrupador' in linha.get_attribute('class'):
                    codigo = linha.text.split(' ')[0]
                    i += 1
                    continue

                while i < len(linhas_turmas) and 'agrupador' not in linhas_turmas[i].get_attribute('class'):
                    print(linhas_turmas[i].text.upper())
                    texto = re.sub(r'\(\d+h\)', '', linhas_turmas[i].text)
                    match = self.regex_turma.search(texto)
                    if match:
                        resultado = match.groupdict()
                        professores = resultado['docente'].strip().split('\n')

                        codigo_lugar = db.execute_fetchone("""
                            SELECT inserir_lugar(%s)
                        """, (resultado['local'],))[0]

                        db.execute_commit("""
                            SELECT inserir_oferta(%s::CodigoDisciplina, %s::NUMERIC, %s::SMALLINT, %s::CHAR(30), %s::CHAR(30), %s::SMALLINT, %s::SMALLINT, %s::INTEGER, %s::TEXT[]);
                        """, (
                            codigo,
                            float(resultado['periodo']),
                            int(resultado['turma']),
                            resultado['horario'],
                            resultado['complemento_horario'],
                            int(resultado['vagas_total']),
                            int(resultado['vagas_ocupadas']),
                            codigo_lugar,
                            professores,
                        ))

                    else:
                        print("ERRO: ", linhas_turmas[i].text)
                    i += 1
        except NoSuchElementException:
            print("A div com ID 'turmasAbertas' não foi encontrada.")

    def atualiza_unidade(self, driver):
        self.turmas_encontradas = []
        self.escolher_nivel(driver)
        self.escolhe_unidade(driver)
        self.buscar(driver)
        self.buscar_info_materias(driver)
        try:
            painel_erros = driver.find_element(By.ID, 'painel-erros')
            if painel_erros.is_displayed():
                time.sleep(2)
                return
        except NoSuchElementException:
            pass
        self.insere_oferta(driver)
        self.insere_disciplina(driver)
        self.insere_oferta(driver)

    def getPage(self):
        self.contador_proxies += 1
        self.contador_proxies % len(proxies)

        service = Service()
        options = webdriver.ChromeOptions()
        # options.add_argument(f'--proxy-server={proxies[self.contador_proxies]}')
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        self.set_unidades(driver)
        for _ in self.unidades:
            self.atualiza_unidade(driver)

        driver.quit()


scraper = SigaaScraper()
db.connect()
# threads = []
# for _ in range(5):
#     thread = threading.Thread(target=scraper.getPage)
#     thread.start()
#     threads.append(thread)
#
# for thread in threads:
#     thread.join()
scraper.getPage()
db.close()