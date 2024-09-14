import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import psycopg2

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
        self.contador_proxies = 0
        self.proxy = proxies[0]
        self.timeout = 1.5
        self.unidades = []
        self.contador_unidades = 3
        self.turmas_encontradas = []
        self.contador_turmas = 0
        self.regex_turma = re.compile(
            r'^(?P<turma>\d{2})\s+'  # Captura o número da turma (2 dígitos)
            r'(?P<periodo>\d{4}\.\d)\s+'  # Captura o período no formato XXXX.X
            r'(?P<docente>(?:[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ]+ ?(?:\(\d+h\))?\n?)+)'  # Captura um ou mais docentes (inclui possível quebra de linha)
            r'\n?(?P<horario>\w+\s?\(?\d{2}/\d{2}/\d{4} - \d{2}/\d{2}/\d{4}\)?\s*)?'  # Captura o horário e a data (ou permite ausência de data)
            r'(?P<vagas_total>\d+)\s+'  # Captura o número total de vagas
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

    def insere_disciplina(self, driver):
        for turma in self.turmas_encontradas:
            time.sleep(2)
            try:
                elemento = WebDriverWait(driver, self.timeout).until(
                    EC.element_to_be_clickable((By.ID, turma))
                )
                driver.execute_script("arguments[0].click();", elemento)
                WebDriverWait(driver, self.timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                curso_info = {
                    'nome': '',
                    'codigo': '',
                    'descricao': '',
                    'modalidade': '',
                    'pre_requisitos': '',
                    'coequivalencia': '',
                    'equivalencia': ''
                }

                linhas = driver.find_elements(By.TAG_NAME, 'tr')
                for linha in linhas:
                    th_elements = linha.find_elements(By.TAG_NAME, 'th')
                    if th_elements:
                        th_texto = th_elements[0].text.strip()

                        if th_texto == "Nome:":
                            curso_info['nome'] = linha.find_element(By.TAG_NAME, 'td').text.strip()
                        elif th_texto == "Código:":
                            curso_info['codigo'] = linha.find_element(By.TAG_NAME, 'td').text.strip()
                        elif th_texto == "Ementa/Descrição:":
                            curso_info['descricao'] = linha.find_element(By.TAG_NAME, 'td').text.strip()
                        elif th_texto == "Modalidade de Educação:":
                            curso_info['modalidade'] = linha.find_element(By.TAG_NAME, 'td').text.strip()
                        elif th_texto == "Pré-Requisitos:":
                            curso_info['pre_requisitos'] = linha.find_element(By.TAG_NAME, 'td').text.strip()
                        elif th_texto == "Co-Requisitos:":
                            curso_info['coequivalencia'] = linha.find_element(By.TAG_NAME, 'td').text.strip()
                        elif th_texto == "Equivalências:":
                            curso_info['equivalencia'] = linha.find_element(By.TAG_NAME, 'td').text.strip()

                db.execute_commit("""
                    INSERT INTO disciplina (codigo, modalidade, nome, descricao)
                    VALUES (%s, %s, %s, %s);
                """, (curso_info['codigo'], curso_info['modalidade'], curso_info['nome'],
                      curso_info['descricao'],))

                db.execute_commit("""
                    INSERT INTO requisitos (codigo, equivalencia, prerequisito, coequivalencia)
                    VALUES (%s, %s, %s, %s);
                """, (curso_info['codigo'], curso_info['pre_requisitos'],
                    curso_info['coequivalencia'], curso_info['equivalencia'],))

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
                    texto = re.sub(r'\(\d+h\)', '', linhas_turmas[i].text)
                    match = self.regex_turma.search(texto)
                    if match:
                        resultado = match.groupdict()
                        professores = resultado['docente'].strip().split('\n')
                        resultado['docente'] = ', '.join(professores).strip()
                        # db.execute_commit("""
                        #         INSERT INTO disciplina_ofertada (codigo, periodo, turma, docente, horario, vagas_total, vagas_ocupadas, local)
                        #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        #     """, (
                        #     codigo,
                        #     float(resultado['periodo']),
                        #     int(resultado['turma']),
                        #     resultado['docente'],
                        #     resultado['horario'],
                        #     int(resultado['vagas_total']),
                        #     int(resultado['vagas_ocupadas']),
                        #     resultado['local']
                        # ))
                        print(resultado)
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
        # self.insere_disciplina(driver)
        self.insere_oferta(driver)

    def getPage(self):
        service = Service()
        options = webdriver.ChromeOptions()
        # options.add_argument(f'--proxy-server={self.proxy}')
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)

        self.set_unidades(driver)
        for _ in self.unidades:
            self.atualiza_unidade(driver)
        driver.quit()
        return

scraper = SigaaScraper()
db.connect()
scraper.getPage()
db.close()