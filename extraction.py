from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import chromedriver_autoinstaller
import pandas as pd
import requests
import os

# Tempo máximo de espera (em segundos)
timeout = 20

# Configuração inicial
BASE_URL = "https://app.qrcodekit.com"
LOGIN_URL = f"{BASE_URL}/en/login"
TABLE_URL = f"{BASE_URL}/panel/51436/project/list"
OUTPUT_FOLDER = "csv_files"

# Credenciais
EMAIL = "ti.desenvolvimento@ems.com.br"
PASSWORD = "WEwewq@@@241#@123"

# Inicializando o navegador
chrome_options = Options()
chrome_options.add_argument("--headless")

# Instala automaticamente o chromedriver
chromedriver_autoinstaller.install()

# Inicializa o navegador
print(f"Iniciando o navegador (", datetime.now(), ")")
driver = webdriver.Chrome(options=chrome_options)
driver.get(LOGIN_URL)

# Login
print(f"Fazendo login")
driver.find_element(By.NAME, "_username").send_keys(EMAIL)
driver.find_element(By.NAME, "_password").send_keys(PASSWORD)
driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Aguarda até que a tabela com data-cy="projects.table" seja renderizada
try:
    print(f"Aguardando renderização da tabela com os projetos")
    table_element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="projects.table"]'))
    )    
except Exception as e:
    print(f"Erro ao aguardar renderização da tabela: {e}")
    driver.quit()

# Extração de links da tabela
print(f"Iniciando extração dos links dos projetos")
rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
project_links = []
for row in rows:
    try:
        link = row.find_element(By.CSS_SELECTOR, "td span.title a").get_attribute("href")
        project_links.append(link)
    except:
        continue

# Criação da pasta de saída
print(f"Criando diretório de saída")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Obter os cookies do Selenium
selenium_cookies = driver.get_cookies()

# Converter cookies do Selenium para o formato do requests
cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}

# Download de CSVs
print(f"Baixando CSVs")
for link in project_links:
    driver.get(link)
    
    # Aguarda até que o link de exportação dos qrcodes seja renderizado
    try:
        export_link_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Exportar CSV"))
        )        
    except Exception as e:
        print(f"Erro ao aguardar a renderização do link de exportação: {e}")
        driver.quit()

    try:
        export_link = driver.find_element(By.LINK_TEXT, "Exportar CSV").get_attribute("href")        
        # Baixar o CSV usando os cookies
        csv_response = requests.get(export_link, cookies=cookies)
        # Salvar o arquivo somente se a resposta for válida
        if csv_response.status_code == 200 and 'application/csv' in csv_response.headers.get('Content-Type', ''):
            filename = os.path.join(OUTPUT_FOLDER, export_link.split("/")[6] + ".csv")            
            with open(filename, "wb") as f:
                f.write(csv_response.content)
        else:
            print(f"Erro ao baixar o arquivo CSV de {export_link}. Resposta: {csv_response.status_code}")
    except:
        print(f"Erro ao baixar CSV de {link}")

# Combinação de dados
print(f"Combinando dados de todos os CSVs")
all_data = []
for csv_file in os.listdir(OUTPUT_FOLDER):
    if csv_file.endswith(".csv"):
        df = pd.read_csv(os.path.join(OUTPUT_FOLDER, csv_file))
        df = df.replace(",", ";", regex=True)
        all_data.append(df[["QR ID", "QR Description", "Permalink", "Redirection"]])        

# Combina os dados em um único DataFrame
final_df = pd.concat(all_data, ignore_index=True)

# Salva o arquivo combinado
print(f"Salvando dados em um único arquivo")
os.makedirs(OUTPUT_FOLDER + '\combined_data', exist_ok=True)
combined_file_path = os.path.join(OUTPUT_FOLDER + '\combined_data', "combined_data.csv")
final_df.to_csv(combined_file_path, index=False, sep=";")

print(f"Dados combinados salvos em 'combined_data.csv'.")
print(f"Finalizando processo de extração (", datetime.now(), ")")

# Finaliza o navegador
driver.quit()