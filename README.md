# Anime Sama Downloader GUI
## Lancement
Via ``uv`` sur Windows :
````
$env:PYTHONPATH="." ; uv run python -m gui

uv run -m src.gui
````

Via ``Docker`` :
````
docker run --rm `
  -e APP_HOST="0.0.0.0" `
  -e APP_PORT=8080 `
  -e APP_RELOAD="false" `
  -e TZ="Europe/Paris" `
  -p 8080:8080 `
  flastar/anime-sama-downloader-gui
````

N'hésitez pas à rajouter un volume également.

Utilisation de l'IA :
- Quasi totalité du frontend réalisé par l'IA
- 50-60% du backend par IA (chaque fonction individuellement, la structure a bien été réalisée par un humain)
