import streamlit as st
import pandas as pd
from google import genai
from PIL import Image
import io

st.set_page_config(page_title="Super Robot Saisie IA", layout="wide")
st.title("🤖 Super Robot de Saisie & Classification d'État Civil")

# Configuration de la clé API sécurisée
api_key = st.sidebar.text_input("Saisissez votre clé API Google Gemini (Gratuite) :", type="password")

uploaded_files = st.file_uploader("Importez vos documents (Photos d'actes, Registres, max 60 pages) :", 
                                  type=["png", "jpg", "jpeg", "pdf"], 
                                  accept_multiple_files=True)

if uploaded_files and api_key:
    if st.button("🚀 Lancer la Saisie Automatique par l'IA"):
        client = genai.Client(api_key=api_key)
        all_data = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, file in enumerate(uploaded_files):
            status_text.text(f"Analyse du document {index + 1}/{len(uploaded_files)} en cours...")
            # Lecture et conversion correcte de l'image pour Gemini
image_bytes = file.read()
image_pil = Image.open(io.BytesIO(image_bytes))

prompt = """
Analyse cette image d'acte d'état civil ancien. Extrais les informations de manière TRÈS PRÉCISE, sans inventer de texte et sans faire de faute de frappe. 
Identifie le type d'acte et extrait les informations clés.
Réponds UNIQUEMENT sous la forme d'une ligne de texte brute avec les éléments séparés par le symbole '|' comme ceci :
Type d'acte | Nom de famille | Prénoms | Date de l'événement | Noms des parents ou conjoints
Si une information est totalement illisible, écris 'Inconnu'. Ne mets aucun autre texte dans ta réponse.
"""

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[image_pil, prompt]
    )

                )
                
                # Découpage du résultat de l'IA
                resultat = response.text.strip().split('|')
                if len(resultat) >= 5:
                    all_data.append({
                        "Type d'acte": resultat[0].strip(),
                        "Nom": resultat[1].strip().upper(), # Nom en majuscule
                        "Prénoms": resultat[2].strip(),
                        "Date Événement": resultat[3].strip(),
                        "Parents / Conjoints": resultat[4].strip()
                    })
            except Exception as e:
                st.error(f"Erreur sur le fichier {file.name} : {e}")
                
            progress_bar.progress((index + 1) / len(uploaded_files))
            
        status_text.text("✅ Traitement de tous les documents terminé !")
        
        # Création du tableau Excel de synthèse
        if all_data:
            df = pd.DataFrame(all_data)
            st.write("### 📊 Aperçu des données classifiées (Zéro faute de recopie) :")
            st.dataframe(df)
            
            # Bouton de téléchargement Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Saisie_Etat_Civil')
            xlsx_data = output.getvalue()
            
            st.download_button(
                label="📥 Télécharger le registre complet sur Excel",
                data=xlsx_data,
                file_name="registre_saisie_ia.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
elif uploaded_files and not api_key:
    st.warning("⚠️ Veuillez inscrire votre clé API gratuite Gemini dans la barre latérale gauche pour activer le robot.")
