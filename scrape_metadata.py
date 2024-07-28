import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

# Initialize the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = f"https://memoria.bn.gov.br/docreader/docmulti.aspx?bib={config.NEWSPAPER_ID}"
driver.get(url)

def close_popup():
    close_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'rwCloseButton'))
    )
    close_button.click()
    time.sleep(5)  # Wait for the popup to close

def extract_data_from_popup():
    # Switch to the iframe containing the desired content
    iframe = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//iframe[@name="ListaOcorRadWindow"]'))
    )
    driver.switch_to.frame(iframe)
    # print("Switched to iframe")

    # Now search for elements containing the text "ano" and "edição" within the iframe
    rows = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, '//a[contains(text(), "ano")]'))
    )

    data = []
    for row in rows:
        folder_text = row.text
        # print(f"Found text: {folder_text}")  # Debugging: print each found text
        data.append(folder_text)
    
    driver.switch_to.default_content()  # Switch back to the main content
    return data

def perform_search_and_extract(search_term):
    # Input the search term and submit
    search_input = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.NAME, 'PesquisarTxt')))
    search_input.clear()
    time.sleep(10)
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.ENTER)
    time.sleep(20)

    # Wait for the search results table to load
    periods_table = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'ListaRadGrid_ctl00'))
    )

    all_data = []
    rows = periods_table.find_elements(By.XPATH, './/tr[contains(@class, "rgRow") or contains(@class, "rgAltRow")]')

    for index, row in enumerate(rows):
        period_name = row.find_element(By.XPATH, './/td[1]').text
        matches_value = row.find_elements(By.XPATH, './/td')[3].text
        print(f"Processing period: {period_name} with matches: {matches_value}")

        if matches_value == "0":
            print(f"Skipping period: {period_name} as it has 0 matches")
            continue

        button_img = row.find_element(By.XPATH, './/img[@id="BibMaisButton"]')

        # Perform the hover action using ActionChains
        actions = ActionChains(driver)
        actions.move_to_element(button_img).perform()
        print(f"Hovered over button_img for period: {period_name}")

        try:
            matches_list_option = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'Match list...'))
            )
            matches_list_option.click()
            print(f"Clicked on 'Match list...' option for period: {period_name}")
            time.sleep(10)

            # Extract data from the popup
            period_data = extract_data_from_popup()
            for data in period_data:
                all_data.append({'Full_ID': data, 'Word': search_term})

            # Close the popup
            close_popup()
        except Exception as e:
            print(f"No 'Match list...' option for period: {period_name}. Skipping...")
            continue

    return all_data

search_terms = config.SEARCH_TERMS
final_data = []

for term in search_terms:
    print(f"Processing search term: {term}")
    data = perform_search_and_extract(term)
    final_data.extend(data)

# Convert the extracted data to a DataFrame
df = pd.DataFrame(final_data)
df['Newspaper'] = config.NEWSPAPER_ID_DICT[config.NEWSPAPER_ID]
print(df)

# Write the DataFrame to a CSV file
df.to_csv(config.OUTPUT_FILE, index=False)
print("Data written to " + config.OUTPUT_FILE)

driver.quit()
