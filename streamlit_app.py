#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cyber-Mosaïque v1.0 - Streamlit Web App
Interface Web interactive pour la cybersécurité éducative
"""

import streamlit as st
import random
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import re

# Configuration Streamlit
st.set_page_config(
    page_title="🛡️ Cyber-Mosaïque",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Seed pour reproductibilité
SEED_CONSTANT = 2025
random.seed(SEED_CONSTANT)

# Répertoire de logs
RESULTS_DIR = Path("results")
LOG_FILE = RESULTS_DIR / "eval_trace.log"
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# SYSTÈME DE LOGGING
# ============================================================================

def log_action(action: str, details: Dict = None):
    """Enregistre une action utilisateur."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] ACTION: {action}\n"
    
    if details:
        log_entry += f"  Détails: {json.dumps(details, ensure_ascii=False, indent=2)}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)


def log_result(quiz_result: Dict):
    """Enregistre les résultats du quiz."""
    timestamp = datetime.now().isoformat()
    log_entry = f"\n{'='*50}\n"
    log_entry += f"[{timestamp}] RÉSULTATS DU QUIZ\n"
    log_entry += f"Score: {quiz_result['score']}/{quiz_result['total']}\n"
    log_entry += f"Pourcentage: {quiz_result['percentage']:.1f}%\n"
    log_entry += f"{'='*50}\n\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)


# Initialiser le log au premier chargement
if not LOG_FILE.exists():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== CYBER-MOSAÏQUE - Démarrage ===\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Seed: {SEED_CONSTANT}\n")
        f.write(f"{'='*50}\n\n")

# ============================================================================
# DONNÉES DES SCÉNARIOS
# ============================================================================

SCENARIOS = [
    {
        "id": 1,
        "titre": "🚨 Phishing MonCash",
        "emoji": "📱",
        "scenario": """
        Vous recevez un SMS urgent:
        
        > **"URGENT: Votre compte MonCash est bloqué. 
        > Cliquez ici pour débloquer: http://moncash-secure-2025.tk"**
        """,
        "question": "Que faites-vous?",
        "options": [
            {
                "text": "Cliquer immédiatement sur le lien",
                "correct": False,
                "feedback": "❌ DANGER! C'est du phishing. Le lien est frauduleux."
            },
            {
                "text": "Vérifier avec MonCash directement",
                "correct": True,
                "feedback": "✅ CORRECT! Toujours vérifier via le site officiel."
            },
            {
                "text": "Ignorer et continuer",
                "correct": False,
                "feedback": "❌ Risqué. Il faut vérifier si c'est légitime."
            },
            {
                "text": "Partager le lien à des amis",
                "correct": False,
                "feedback": "❌ GRAVE! Cela propage la menace."
            }
        ],
        "relevance": "Les services de paiement mobiles sont très utilisés en Haïti.",
        "confidence": "Vous pouvez toujours contacter le service directement."
    },
    {
        "id": 2,
        "titre": "🎓 Faux Lien de Bourse",
        "emoji": "📧",
        "scenario": """
        Vous recevez un email:
        
        > **De:** scholarship@minesantos-ht.com  
        > **Objet:** Félicitations! Bourse $5000  
        > "Cliquez ici pour compléter votre inscription avant le 25/02:
        > http://b0urses-minesantos-2025.tk"
        """,
        "question": "Quel est votre réflexe?",
        "options": [
            {
                "text": "Remplir le formulaire immédiatement",
                "correct": False,
                "feedback": "❌ PIÈGE! Domaine .tk frauduleux, email non officiel."
            },
            {
                "text": "Vérifier l'adresse email et le domaine",
                "correct": True,
                "feedback": "✅ CORRECT! Chercher les indicateurs de fraude."
            },
            {
                "text": "Entrer vos identifiants personnels",
                "correct": False,
                "feedback": "❌ CRITIQUE! Vol d'identité assuré."
            },
            {
                "text": "Transférer à la banque",
                "correct": False,
                "feedback": "❌ Les bourses ne passent pas par les banques ainsi."
            }
        ],
        "relevance": "Les arnaqueurs ciblent les étudiants avec des fausses bourses.",
        "confidence": "Vérifiez TOUJOURS le domaine email officiel."
    },
    {
        "id": 3,
        "titre": "💻 Clé USB Suspecte",
        "emoji": "🔌",
        "scenario": """
        Vous travaillez dans un cybercafé et trouvez une clé USB sur le bureau
        avec écrit "Résultats d'examen 2026".
        
        Vous l'insérez pour voir ce qu'il y a...
        """,
        "question": "Avez-vous bien agi?",
        "options": [
            {
                "text": "Non, c'est extrêmement dangereux",
                "correct": True,
                "feedback": "✅ CORRECT! C'est une technique courante de distribution de malware."
            },
            {
                "text": "Oui, c'est juste une clé USB",
                "correct": False,
                "feedback": "❌ GRAVE! Elle pourrait contenir un virus ou trojan."
            },
            {
                "text": "C'est sans risque dans un cybercafé",
                "correct": False,
                "feedback": "❌ FAUX! Les cybercafés sont des cibles privilégiées."
            },
            {
                "text": "Il faut la brancher sur un autre ordinateur",
                "correct": False,
                "feedback": "❌ Cela propage juste le malware davantage."
            }
        ],
        "relevance": "Les cybercafés haïtiens manquent souvent de sécurité.",
        "confidence": "Ne jamais connecter de clés USB inconnues."
    }
]

# ============================================================================
# MOTEUR DE DIAGNOSTIC
# ============================================================================

class MoteurDiagnostic:
    def __init__(self):
        self.threat_signatures = {
            "phishing": {
                "patterns": [
                    r"(?:http|https)://[^\s]*\.tk",
                    r"(?:http|https)://[^\s]*bit\.ly",
                ],
                "severity": "HIGH",
                "description": "Tentative de phishing"
            },
            "credential_harvesting": {
                "patterns": [
                    r"password\s*[:=]",
                    r"mot de passe",
                    r"login\s*form",
                ],
                "severity": "CRITICAL",
                "description": "Vol de credentials"
            },
            "malware": {
                "patterns": [
                    r"\.exe",
                    r"\.scr",
                    r"\.bat",
                ],
                "severity": "CRITICAL",
                "description": "Code malveillant"
            }
        }
        
        self.sample_logs = [
            "2026-02-23 10:15:32 INFO: Utilisateur 'jean_haiti' connecté",
            "2026-02-23 10:16:45 WARNING: Tentative d'accès URL: http://moncash-secure-2025.tk",
            "2026-02-23 10:17:12 INFO: Email reçu de: scholarship@minesantos-ht.com",
            "2026-02-23 10:18:00 ERROR: Clé USB inconnue détectée",
            "2026-02-23 10:18:45 CRITICAL: Fichier .exe détecté sur clé USB: autorun.exe",
            "2026-02-23 10:19:20 INFO: Antivirus scan lancé",
            "2026-02-23 10:22:15 ALERT: 3 fichiers malveillants identifiés",
        ]
    
    def scanner_logs(self):
        results = {
            "total_lines": len(self.sample_logs),
            "threats_found": [],
            "severity_summary": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0},
        }
        
        for line_num, log_line in enumerate(self.sample_logs, 1):
            for threat_type, threat_info in self.threat_signatures.items():
                for pattern in threat_info["patterns"]:
                    if re.search(pattern, log_line, re.IGNORECASE):
                        threat = {
                            "type": threat_type,
                            "line": line_num,
                            "log": log_line,
                            "severity": threat_info["severity"],
                            "description": threat_info["description"]
                        }
                        results["threats_found"].append(threat)
                        results["severity_summary"][threat_info["severity"]] += 1
                        break
        
        return results

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def main():
    # Sidebar Navigation
    st.sidebar.title("🛡️ CYBER-MOSAÏQUE")
    st.sidebar.write("v1.0 - Résilience numérique pour Haiti")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "📋 Navigation",
        ["🏠 Accueil", "🎯 Quiz", "🔍 Diagnostic", "📊 Résultats", "ℹ️ À propos"]
    )
    
    if page == "🏠 Accueil":
        page_accueil()
    elif page == "🎯 Quiz":
        page_quiz()
    elif page == "🔍 Diagnostic":
        page_diagnostic()
    elif page == "📊 Résultats":
        page_resultats()
    elif page == "ℹ️ À propos":
        page_apropos()


def page_accueil():
    st.title("🛡️ CYBER-MOSAÏQUE")
    st.subheader("Renforcer la résilience numérique des étudiants haïtiens")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://via.placeholder.com/300x200?text=CyberSecurity", 
                use_column_width=True)
    
    with col2:
        st.markdown("""
        ## Bienvenue! 👋
        
        Cyber-Mosaïque est une application éducative conçue pour:
        
        ✅ **Sensibiliser** aux menaces cybersécurité réelles  
        ✅ **Développer** vos réflexes de sécurité  
        ✅ **Tester** vos connaissances avec des scénarios réalistes  
        
        ### Fonctionnalités:
        - 🎯 Quiz interactif (modèle ARCS)
        - 🔍 Diagnostic de sécurité
        - 📊 Suivi de vos progrès
        - 🌐 Mode hors-ligne complet
        """)
    
    st.markdown("---")
    st.info("""
    💡 **Conseil:** Commencez par le **Quiz** pour tester vos connaissances!
    """)


def page_quiz():
    st.title("🎯 QUIZ INTERACTIF")
    st.write("Testez vos réflexes de sécurité avec des scénarios réalistes!")
    
    # Initialize session state
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.current_scenario = 0
        st.session_state.score = 0
        st.session_state.responses = []
        st.session_state.scenarios = random.sample(SCENARIOS, len(SCENARIOS))
    
    if not st.session_state.quiz_started:
        st.markdown("""
        ## Comment ça marche?
        
        1. 📖 Vous recevrez 3 scénarios de cybersécurité
        2. ❓ Pour chaque scénario, choisissez la bonne réaction
        3. 📊 Vous obtiendrez un score à la fin
        4. 📝 Vos réponses seront enregistrées
        
        **Durée estimée:** 5-10 minutes
        """)
        
        if st.button("🚀 Démarrer le Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_started = True
            log_action("Démarrage du quiz")
            st.rerun()
    else:
        # Quiz in progress
        if st.session_state.current_scenario < len(st.session_state.scenarios):
            scenario = st.session_state.scenarios[st.session_state.current_scenario]
            
            st.markdown(f"### Scénario {st.session_state.current_scenario + 1}/3")
            st.markdown(f"## {scenario['emoji']} {scenario['titre']}")
            
            # Progress bar
            progress = (st.session_state.current_scenario + 1) / len(st.session_state.scenarios)
            st.progress(progress)
            
            st.markdown(scenario['scenario'])
            st.markdown(f"### ❓ {scenario['question']}")
            
            # Options as buttons
            cols = st.columns(1)
            selected_option = None
            
            for idx, option in enumerate(scenario['options']):
                if st.button(
                    f"{idx + 1}. {option['text']}", 
                    use_container_width=True,
                    key=f"option_{st.session_state.current_scenario}_{idx}"
                ):
                    selected_option = idx
            
            if selected_option is not None:
                option = scenario['options'][selected_option]
                
                # Show feedback
                if option['correct']:
                    st.success(option['feedback'])
                    st.session_state.score += 1
                else:
                    st.error(option['feedback'])
                
                # Additional context
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"💡 **Contexte:** {scenario['relevance']}")
                with col2:
                    st.warning(f"💪 **Conseil:** {scenario['confidence']}")
                
                # Log the response
                response = {
                    "scenario": scenario["id"],
                    "user_choice": selected_option + 1,
                    "correct": option['correct'],
                    "option_selected": option['text']
                }
                st.session_state.responses.append(response)
                log_action(f"Réponse scénario {scenario['id']}", response)
                
                # Next button
                col1, col2 = st.columns([1, 1])
                with col2:
                    if st.button("➡️ Scénario suivant", use_container_width=True, type="primary"):
                        st.session_state.current_scenario += 1
                        st.rerun()
        else:
            # Quiz finished
            st.balloons()
            st.success("🎉 Quiz terminé!")
            
            # Results
            percentage = (st.session_state.score / len(st.session_state.scenarios)) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{st.session_state.score}/{len(st.session_state.scenarios)}")
            with col2:
                st.metric("Pourcentage", f"{percentage:.1f}%")
            with col3:
                if percentage >= 80:
                    st.metric("Niveau", "🏅 Excellent")
                elif percentage >= 60:
                    st.metric("Niveau", "✅ Bon")
                else:
                    st.metric("Niveau", "📚 À améliorer")
            
            # Feedback
            st.markdown("---")
            if percentage >= 80:
                st.info("🏅 **EXCELLENT!** Vous avez une excellente compréhension!")
            elif percentage >= 60:
                st.info("✅ **BON TRAVAIL!** Vous maîtrisez les bases.")
            else:
                st.warning("⚠️ **À AMÉLIORER.** Relisez les conseils et réessayez!")
            
            # Log results
            result = {
                "score": st.session_state.score,
                "total": len(st.session_state.scenarios),
                "percentage": percentage,
                "responses": st.session_state.responses
            }
            log_result(result)
            
            # Restart button
            if st.button("🔄 Recommencer le quiz", use_container_width=True):
                st.session_state.quiz_started = False
                st.session_state.current_scenario = 0
                st.session_state.score = 0
                st.session_state.responses = []
                st.rerun()


def page_diagnostic():
    st.title("🔍 DIAGNOSTIC DE SÉCURITÉ")
    st.write("Simulation d'un scanner de logs pour détecter les menaces")
    
    if st.button("🚀 Lancer le scan", use_container_width=True, type="primary"):
        motor = MoteurDiagnostic()
        results = motor.scanner_logs()
        
        log_action("Diagnostic logs", {
            "total_lines": results["total_lines"],
            "threats": len(results["threats_found"])
        })
        
        # Display results
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Lignes analysées", results['total_lines'])
        with col2:
            st.metric("Menaces trouvées", len(results['threats_found']))
        with col3:
            st.metric("🔴 Critique", results['severity_summary']['CRITICAL'])
        with col4:
            st.metric("🟠 Élevée", results['severity_summary']['HIGH'])
        
        st.markdown("---")
        
        if results['threats_found']:
            st.subheader("📋 Détails des menaces détectées:")
            for idx, threat in enumerate(results['threats_found'], 1):
                with st.expander(f"{idx}. [{threat['severity']}] {threat['description']}", expanded=True):
                    st.write(f"**Type:** {threat['type']}")
                    st.write(f"**Ligne:** {threat['line']}")
                    st.code(threat['log'], language="log")
        else:
            st.success("✅ Aucune menace détectée!")


def page_resultats():
    st.title("📊 VOS RÉSULTATS")
    
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        st.write("📄 **Historique de vos actions enregistrées:**")
        st.code(content, language="log")
        
        # Download button
        st.download_button(
            label="📥 Télécharger le log",
            data=content,
            file_name=f"eval_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            mime="text/plain"
        )
    else:
        st.info("📭 Aucun résultat enregistré. Lancez le quiz pour commencer!")


def page_apropos():
    st.title("ℹ️ À PROPOS")
    
    st.markdown("""
    ## 🛡️ Cyber-Mosaïque v1.0
    
    Application de renforcement de la résilience numérique pour étudiants haïtiens.
    
    ### 🎯 Objectifs:
    - Sensibiliser aux menaces cybersécurité réelles
    - Développer les réflexes de sécurité
    - Proposer des scénarios contextualisés haïtiens
    
    ### 📋 Caractéristiques:
    - ✅ Quiz interactif basé sur le modèle ARCS
    - ✅ Diagnostic de sécurité (simulation de scan de logs)
    - ✅ Mode Zero-Data (fonctionne hors-ligne)
    - ✅ Compatible tous les appareils
    - ✅ Aucune dépendance externe
    
    ### ⚙️ Configuration technique:
    - **Langage:** Python 3.7+
    - **Framework:** Streamlit
    - **Seed:** 2025 (pour reproductibilité)
    - **Logs:** results/eval_trace.log
    
    ### 📧 Support:
    Pour toute question, consultez votre responsable éducatif.
    
    ---
    **Version:** 1.0  
    **Date:** 2026-02-23  
    **Licence:** MIT
    """)


if __name__ == "__main__":
    main()