import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def find_element_with_retry(driver, by, value, max_attempts=3, delay=2):
    """Tente de trouver un élément plusieurs fois avec un délai entre chaque tentative"""
    for attempt in range(max_attempts):
        try:
            element = driver.find_element(by=by, value=value)
            print(f"Élément trouvé: {value}")
            return element
        except Exception as e:
            print(f"Tentative {attempt + 1}/{max_attempts} échouée pour {value}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
            else:
                raise e
    return None

def test_whatsapp():
    try:
        # Configuration et lancement du driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get("https://web.whatsapp.com")
        
        print("\nVeuillez scanner le QR Code avec votre téléphone")
        print("et appuyer sur Entrée une fois que vous êtes connecté...")
        input()
        print("Vous êtes maintenant connecté!")
        time.sleep(5)  # Attente plus longue après la connexion
        
        # Demander le nom du contact/groupe
        contact_name = input("\nEntrez le nom du contact ou du groupe: ").strip()
        
        print("\nRecherche de la barre de recherche...")
        # Utiliser le data-tab="3" trouvé dans le diagnostic
        search_box = find_element_with_retry(
            driver,
            By.CSS_SELECTOR,
            'div[contenteditable="true"][data-tab="3"]'
        )
        
        if not search_box:
            raise Exception("Impossible de trouver la barre de recherche")
            
        print("Clic sur la barre de recherche...")
        search_box.click()
        time.sleep(2)
        
        print(f"Recherche de '{contact_name}'...")
        search_box.clear()
        search_box.send_keys(contact_name)
        time.sleep(3)
        
        print("Recherche du contact dans les résultats...")
        contact_xpath = f"//span[@title='{contact_name}']"
        contact = find_element_with_retry(driver, By.XPATH, contact_xpath)
        contact.click()
        time.sleep(2)
        
        print("Préparation du message...")
        message = "Ceci est un message de test ce n'est pas joan mais un bot en vue de d'envoyer automatiquement la draft"  # Sans emoji
        # Utiliser le data-tab="10" trouvé dans le diagnostic
        message_box = find_element_with_retry(
            driver,
            By.CSS_SELECTOR,
            'div[contenteditable="true"][data-tab="10"]'
        )
                
        if not message_box:
            raise Exception("Impossible de trouver la zone de message")
            
        print("Envoi du message...")
        message_box.click()
        message_box.send_keys(message)
        time.sleep(1)
        message_box.send_keys(Keys.ENTER)
        
        print("Message envoyé avec succès!")
        input("\nAppuyez sur Entrée pour fermer le navigateur...")
        
    except Exception as e:
        print(f"\nUne erreur est survenue: {str(e)}")
        
        if 'driver' in locals():
            print("\nTentative de diagnostic...")
            try:
                # Rechercher tous les éléments contenteditable
                elements = driver.find_elements(By.CSS_SELECTOR, '[contenteditable="true"]')
                print(f"\nÉléments contenteditable trouvés: {len(elements)}")
                for i, elem in enumerate(elements):
                    print(f"\nÉlément {i+1}:")
                    print("HTML:", elem.get_attribute('outerHTML'))
                    print("Class:", elem.get_attribute('class'))
                    print("Data-tab:", elem.get_attribute('data-tab'))
            except Exception as diag_error:
                print("Erreur lors du diagnostic:", str(diag_error))
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_whatsapp()