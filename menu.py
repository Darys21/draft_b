import datetime
import time
from draft import Draft
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class WhatsAppDraft:
    # XPATH constants
    SEARCH_BOX_XPATH = '//*[@id="side"]/div[1]/div/label/div/div[2]'
    MESSAGE_BOX_XPATH = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]'
    
    def __init__(self):
        """
        Initialise le gestionnaire de draft WhatsApp.
        """
        self.message_buffer = []
        self.driver = None
        self.group_name = None
        
    def initialize_driver(self):
        """Initialise le driver Selenium et connecte à WhatsApp"""
        try:
            # Configuration et lancement du driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service)
            self.driver.get("https://web.whatsapp.com")
            
            # Attendre la connexion de l'utilisateur
            print("\nVeuillez scanner le QR Code avec votre téléphone")
            print("et appuyer sur Entrée une fois que vous êtes connecté...")
            input()
            print("Vous êtes maintenant connecté!")
            time.sleep(5)  # Attendre que tout soit bien chargé
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation: {e}")
            if self.driver:
                self.driver.quit()
            return False
        
    def connect_to_group(self, group_name: str):
        """Se connecte à un groupe spécifique"""
        try:
            self.group_name = group_name
            
            # Utiliser le data-tab="3" pour la barre de recherche
            search_box = self.driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="3"]')
            search_box.click()
            time.sleep(2)
            
            search_box.clear()
            search_box.send_keys(group_name)
            time.sleep(3)
            
            contact_xpath = f"//span[@title='{group_name}']"
            contact = self.driver.find_element(By.XPATH, contact_xpath)
            contact.click()
            time.sleep(2)
            
            print(f"Connecté au groupe: {self.group_name}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la connexion au groupe: {e}")
            return False
        
    def send_message(self, message: str):
        """Envoie un message dans le groupe"""
        try:
            if not self.group_name:
                print("Aucun groupe sélectionné")
                return False
                
            # Utiliser le data-tab="10" pour la zone de message
            message_box = self.driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]')
            message_box.click()
            message_box.send_keys(message)
            time.sleep(1)
            message_box.send_keys(Keys.ENTER)
            print("Message envoyé avec succès!")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {e}")
            return False
        
    def add_to_buffer(self, message: str):
        """Ajoute un message au buffer."""
        self.message_buffer.append(message)
        if len(self.message_buffer) >= 4:
            self.send_buffer()
    
    def send_buffer(self):
        """Envoie les messages accumulés dans le buffer."""
        if self.message_buffer:
            message = "\n\n".join(self.message_buffer)
            if self.send_message(message):
                self.message_buffer = []
    
    def close(self):
        """Ferme le navigateur"""
        if self.driver:
            self.driver.quit()

def run_draft_with_whatsapp():
    """Lance le processus de draft avec intégration WhatsApp."""
    print("\n=== DRAFT BASKETBALL AVEC INTÉGRATION WHATSAPP ===")
    print("\nAssurez-vous que:")
    print("1. Vous avez Chrome installé")
    print("2. Vous avez votre téléphone à proximité pour scanner le QR code")
    
    try:
        # Initialiser WhatsApp et se connecter
        whatsapp = WhatsAppDraft()
        if not whatsapp.initialize_driver():
            print("Échec de l'initialisation de WhatsApp")
            return
            
        # Une fois connecté, demander le nom du groupe
        print("\nMaintenant que vous êtes connecté à WhatsApp,")
        group_name = input("entrez le nom exact du groupe WhatsApp: ").strip()
        if not group_name:
            print("Le nom du groupe est requis.")
            whatsapp.close()
            return
            
        # Se connecter au groupe
        if not whatsapp.connect_to_group(group_name):
            print("Impossible de trouver le groupe. Vérifiez le nom et réessayez.")
            whatsapp.close()
            return
        
        # Liste des équipes
        equipes = [
            "WILD HOOPS",
            "THE UNDEFEATED",
            "Fear of God Athletics",
            "Ours Boys Academy"
        ]
        
        # Création de l'instance de Draft
        draft = Draft(equipes, whatsapp)
        
        print("\n=== DÉBUT DU DRAFT ===")
        time.sleep(2)
        
        # Premier tour
        input("\nAppuyez sur Entrée pour commencer le premier tour...")
        draft.premier_tour_draft()
        
        # Deuxième tour
        input("\nAppuyez sur Entrée pour commencer le deuxième tour...")
        draft.deuxieme_tour_draft()
        
        # Résultats
        draft.afficher_resultats()
        
        print("\nDraft terminé avec succès!")
        
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")
    finally:
        if 'whatsapp' in locals():
            whatsapp.close()

if __name__ == "__main__":
    run_draft_with_whatsapp()