import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from draft import Draft

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        
    def find_element_with_retry(self, by, value, max_attempts=3, delay=2):
        """Tente de trouver un élément plusieurs fois avec un délai entre chaque tentative"""
        for attempt in range(max_attempts):
            try:
                element = self.driver.find_element(by=by, value=value)
                print(f"Élément trouvé: {value}")
                return element
            except Exception as e:
                print(f"Tentative {attempt + 1}/{max_attempts} échouée pour {value}")
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                else:
                    raise e
        return None

    def initialize_driver(self):
        """Initialise le driver Selenium et connecte à WhatsApp"""
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service)
            self.driver.get("https://web.whatsapp.com")
            
            print("\nVeuillez scanner le QR Code avec votre téléphone")
            print("et appuyer sur Entrée une fois que vous êtes connecté...")
            input()
            print("Vous êtes maintenant connecté!")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Erreur lors de l'initialisation: {e}")
            self.quit()
            return False

    def connect_to_group(self, group_name: str):
        """Se connecte à un groupe WhatsApp"""
        try:
            print(f"\nRecherche du groupe '{group_name}'...")
            search_box = self.find_element_with_retry(
                By.CSS_SELECTOR,
                'div[contenteditable="true"][data-tab="3"]'
            )
            
            if not search_box:
                raise Exception("Impossible de trouver la barre de recherche")
            
            search_box.click()
            time.sleep(2)
            
            search_box.clear()
            search_box.send_keys(group_name)
            time.sleep(3)
            
            contact_xpath = f"//span[@title='{group_name}']"
            contact = self.find_element_with_retry(By.XPATH, contact_xpath)
            contact.click()
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Erreur lors de la connexion au groupe: {e}")
            return False

    def send_message(self, message: str):
        """Envoie un message dans le groupe"""
        try:
            # Nettoyer le message des caractères spéciaux
            message = message.encode('ascii', 'ignore').decode('ascii')
            
            message_box = self.find_element_with_retry(
                By.CSS_SELECTOR,
                'div[contenteditable="true"][data-tab="10"]'
            )
            
            if not message_box:
                raise Exception("Impossible de trouver la zone de message")
            
            message_box.click()
            message_box.send_keys(message)
            time.sleep(1)
            message_box.send_keys(Keys.ENTER)
            print("Message envoyé avec succès!")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {e}")
            return False

    def quit(self):
        """Ferme le navigateur"""
        if self.driver:
            self.driver.quit()
            self.driver = None

def run_draft_with_whatsapp():
    """Lance le processus de draft et envoie les résultats via WhatsApp"""
    whatsapp = WhatsAppBot()
    
    try:
        # Initialiser WhatsApp
        if not whatsapp.initialize_driver():
            print("Échec de l'initialisation de WhatsApp")
            return
        
        # Demander le nom du groupe
        group_name = input("\nEntrez le nom du groupe WhatsApp pour la draft: ").strip()
        if not group_name:
            print("Le nom du groupe est requis")
            return
        
        # Se connecter au groupe
        if not whatsapp.connect_to_group(group_name):
            print("Impossible de se connecter au groupe")
            return
        
        # Initialiser et lancer le draft avec le callback WhatsApp
        equipes = ["WILD HOOPS", "THE UNDEFEATED", "Fear of God Athletics", "Ours Boys Academy"]
        draft = Draft(equipes, whatsapp_callback=whatsapp.send_message)
        
        # Lancer le draft
        draft.premier_tour_draft()
        draft.deuxieme_tour_draft()
        draft.afficher_resultats()
        
    except Exception as e:
        print(f"Une erreur est survenue: {e}")
    finally:
        whatsapp.quit()

if __name__ == "__main__":
    run_draft_with_whatsapp()