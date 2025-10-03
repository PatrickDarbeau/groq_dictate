# Groq Dictate
Un outil Python révolutionnaire pour enregistrer de l'audio depuis le microphone et le transcrire en texte en temps réel à l'aide de l'API Groq Whisper. Transformez votre voix en texte avec une précision remarquable dans une interface intuitive, et insérez-le automatiquement dans l'application de votre choix (Word, Gmail, bloc-note, etc).

## 🚀 Fonctionnalités Avancées

- **🎤 Enregistrement vocal instantané** : Appuyez sur PAUSE pour enregistrer, relâchez pour transcrire
- **🤖 Transcription IA de pointe** : Utilise l'API Groq Whisper pour une transcription précise en français
- **📋 Copie automatique intelligente** : Le texte est automatiquement copié dans le presse-papiers
- **💾 Sauvegarde automatique** : Fichiers audio et transcriptions sauvegardés avec date/heure
- **🎨 Interface graphique moderne** : Interface intuitive avec indicateurs visuels en temps réel
- **⚡ Performance optimisée** : Transcription rapide grâce à l'infrastructure Groq
- **🔒 Sécurité renforcée** : Configuration sécurisée avec variables d'environnement

## 💡 Utilité et Cas d'Utilisation

### **Pour les Professionnels**

- **🎯 Prise de notes rapide** : Transformez vos idées en texte sans taper
- **📝 Rédaction de documents** : Dictez vos emails, rapports et présentations
- **🗣️ Réunions et conférences** : Enregistrez et transcrivez les discussions importantes
- **📚 Étudiants et chercheurs** : Transcrivez des cours, interviews ou conférences

### **Pour la Productivité**

- **⏱️ Gain de temps** : Parlez 3x plus vite que vous ne tapez
- **✍️ Écriture mains libres** : Idéal pour les brainstormings et créations de contenu
- **🔄 Documentation automatique** : Archivez automatiquement vos enregistrements et transcriptions

### **Exemples Concrets d'Utilisation**

1. **Rédaction d'email** : "Enregistrez votre message vocal → Transcription instantanée → Collez dans Outlook"
2. **Prise de notes en réunion** : "Enregistrez la discussion → Obtenez un compte-rendu texte → Partagez avec l'équipe"
3. **Création de contenu** : "Dictez vos idées → Transformez en article/blog → Éditez rapidement"
4. **Apprentissage** : "Enregistrez vos réflexions → Réorganisez vos idées → Structurez votre pensée"

## 🎯 Avantages Clés

- **🚀 Rapidité** : Transcription en quelques secondes seulement
- **🎯 Précision** : Technologie Whisper de Groq pour une reconnaissance vocale avancée
- **💻 Simplicité** : Interface "one-click" avec la touche PAUSE
- **📊 Organisation** : Fichiers automatiquement classés par date et heure
- **🔄 Polyvalence** : Compatible avec toutes les applications (Word, Google Docs, emails, bloc-note, etc.)

## 📋 Prérequis

- Python 3.7+
- Clé API Groq ([Obtenez-la ici](https://console.groq.com/))
- Microphone fonctionnel

## 🔧 Installation

### **Option 1 : Utiliser l'exécutable (Recommandé)**

1. **Télécharger l'exécutable** : Récupérez `Groq Whisperer.exe` depuis la section Releases
  
2. **Créer le fichier de configuration** :
  
  ```bash
  # Copier le fichier d'exemple
  copy .env.example .env
  
  # Éditer le fichier .env et ajouter votre clé API
  # .env
  GROQ_API_KEY=votre_clé_api_groq_ici
  ```
  
3. **Lancer l'application** : Double-cliquez sur `Groq Whisperer.exe`
  

### **Option 2 : Installation depuis les sources**

1. **Cloner le dépôt**
  
  ```bash
  git clone https://github.com/KennyVaneetvelde/groq_whisperer
  cd groq_whisperer
  ```
  
2. **Installer les dépendances**
  
  ```bash
  pip install -r requirements.txt
  ```
  
3. **Configuration de la clé API**
  
  ```bash
  # Copier le fichier d'exemple
  copy .env.example .env
  
  # Éditer le fichier .env et ajouter votre clé API
  # .env
  GROQ_API_KEY=votre_clé_api_groq_ici
  ```
  

### **Construction de l'exécutable (Pour développeurs)**

Si vous souhaitez construire l'exécutable vous-même :

```bash
# Exécuter le script de build
build.bat
# L'exécutable sera créé dans le dossier dist/
```

## 🎯 Utilisation

### **Interface Graphique**

1. **Lancer l'application**
  
  ```bash
  python main.py
  ```
  
2. **Interface principale**
  
  - **Indicateur d'enregistrement** : Affiche l'état (PRÊT/ENREGISTREMENT/TRAITEMENT)
  - **Zone de transcription** : Affiche les logs et le texte transcrit en temps réel
  - **Boutons de contrôle** : Copier, Effacer, Quitter
3. **Enregistrement vocal**
  
  - Appuyez et maintenez la touche **PAUSE** pour démarrer l'enregistrement
  - L'indicateur passe au **ROUGE** pendant l'enregistrement
  - Relâchez la touche **PAUSE** pour arrêter
  - L'indicateur passe à l'**ORANGE** pendant la transcription
  - L'indicateur passe au **vert** pour une nouvelle transcription
4. **Gestion des résultats**
  
  - Le texte est **automatiquement copié** dans le presse-papiers
  - Le texte est **automatiquement inséré** dans votre application cible à l'endroit du curseur
  - Utilisez **Ctrl+V** pour coller dans votre application préférée
  - Les fichiers audio et transcriptions (wav et txt) sont **automatiquement sauvegardés** avec date/heure
5. **Arrêt de l'application**
  
  - Cliquez sur **🚪 Quitter** dans l'interface
  - OU appuyez sur **Ctrl+C** dans la console

### **Workflow Typique**

```
1. Lancez Groq Whisperer en cliquant sur groq_whisperer.bat
2. Ouvrez votre application cible (Word, Gmail, bloc-note, etc.) et cliquez sur le lieu d'insertion
3. Appuyez sur PAUSE et parlez
4. Relâchez PAUSE
5. Vérifiez l'application active et constater le résultat
6. Faites Ctrl+V si vous souhaitez coller à nouveau la transcription 
7. Répétez pour chaque segment de texte
```

## ⚙️ Configuration

Les paramètres de configuration sont définis dans le fichier `main.py` :

```python
# Configuration
MAX_RECORDING_TIME = 300  # 5 minutes maximum
RECORD_KEY = "pause"      # Touche d'enregistrement
AUDIO_SAVE_DIR = "audio"  # Dossier de sauvegarde audio
TEXT_SAVE_DIR = "transcriptions"  # Dossier de sauvegarde des textes 
```

## 📁 Structure du projet

```
groq_whisperer/
├── main.py              # Script principal avec interface graphique
├── requirements.txt     # Dépendances Python
├── .env.example        # Exemple de configuration
├── .env                # Configuration API (à créer)
├── audio/              # Dossier de sauvegarde audio
├── transcriptions/     # Dossier de sauvegarde des textes
├── LICENSE            # Licence EULA
└── README.md          # Documentation complète
```

### **Fichiers de Sauvegarde**

- **Audio** : `recording_2025-03-10_16-34-25.wav` (format date/heure)
- **Transcriptions** : `transcription_2025-03-10_16-34-25.txt` (format date/heure)

## 🔒 Sécurité

- La clé API est stockée dans un fichier `.env` (non versionné)
- Le fichier `.env` est ignoré par Git
- Utilisation de variables d'environnement pour la configuration

## 🐛 Résolution de problèmes

### Erreur "No module named 'dotenv'"

```bash
pip install python-dotenv
```

### Erreur "PortAudio library not found" (Windows)

```bash
pip install pipwin
pipwin install pyaudio
```

### Microphone non détecté

- Vérifiez que votre microphone est connecté et configuré
- Testez votre microphone avec une autre application

## 📄 Licence

Ce projet est sous licence EULA. Voir le fichier `LICENSE` pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

---

**Note** : Assurez-vous d'avoir une connexion Internet active pour utiliser l'API Groq Whisper.
