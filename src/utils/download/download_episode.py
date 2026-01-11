import os
import re
import httpx
import threading

from src.var                            import print_separator, print_status, Colors
from src.utils.download.download_video  import download_video
from src.utils.ts.convert_ts_to_mp4     import convert_ts_to_mp4


# ==================== NOUVELLES FONCTIONNALITÉS MAL ====================
# Cache global pour stocker les résultats de recherche pendant la session
_mal_search_cache = {}
# Verrou pour éviter les appels simultanés
_cache_lock = threading.Lock()


def normalize(text: str) -> str:
    """Normalise un texte pour la comparaison"""
    return re.sub(r"[^\w\s]", "", text.lower().strip())


def _is_movie_title(title: str) -> bool:
    """Détecte si un titre contient des mots-clés indiquant un film"""
    movie_keywords = ["movie", "film", "the movie", "le film"]
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in movie_keywords)


def _get_best_title(anime: dict) -> str:
    """Récupère le meilleur titre disponible (priorité au titre anglais ou par défaut)"""
    titles = anime.get("titles", [])
    
    # Priorité 1: Titre anglais
    for title in titles:
        if title.get("type") == "English":
            return title.get("title", "")
    
    # Priorité 2: Titre par défaut
    for title in titles:
        if title.get("type") == "Default":
            return title.get("title", "")
    
    # Priorité 3: Premier titre disponible
    if titles:
        return titles[0].get("title", "")
    
    # Fallback: titre principal
    return anime.get("title", "Unknown")


def _clean_anime_name(name: str) -> str:
    """Nettoie le nom de l'anime pour améliorer la recherche"""
    # Enlever les suffixes courants qui peuvent gêner la recherche
    name = re.sub(r'\s*\(.*?\)\s*', '', name)  # Enlever les parenthèses et leur contenu
    name = re.sub(r'\s*\[.*?\]\s*', '', name)  # Enlever les crochets et leur contenu
    name = re.sub(r'\s*-\s*saison\s*\d+.*', '', name, flags=re.IGNORECASE)  # Enlever "- Saison X"
    name = re.sub(r'\s*-\s*season\s*\d+.*', '', name, flags=re.IGNORECASE)  # Enlever "- Season X"
    name = re.sub(r'\s*s\d+.*', '', name, flags=re.IGNORECASE)  # Enlever "S1", "S2", etc.
    name = name.strip()
    return name


def _display_search_results(animes: list, query: str) -> dict | None:
    """Affiche les résultats de recherche et demande à l'utilisateur de choisir"""
    if not animes:
        return None
    
    if len(animes) == 1:
        return animes[0]
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}Multiple results found for '{query}':{Colors.ENDC}")
    print_separator()
    
    # Limiter à 10 résultats max
    display_animes = animes[:10]
    
    for idx, anime in enumerate(display_animes, 1):
        anime_type = anime.get("type", "Unknown")
        mal_id = anime.get("mal_id", "?")
        title = _get_best_title(anime)
        
        # Afficher les titres alternatifs
        alt_titles = []
        for t in anime.get("titles", [])[:3]:  # Limiter à 3 titres
            title_text = t.get("title", "")
            if title_text and title_text != title:
                alt_titles.append(title_text)
        
        print(f"{Colors.OKGREEN}[{idx}]{Colors.ENDC} {Colors.BOLD}{title}{Colors.ENDC}")
        print(f"    Type: {anime_type} | MAL ID: {mal_id}")
        if alt_titles:
            print(f"    Alt: {' / '.join(alt_titles[:2])}")
        print()
    
    print(f"{Colors.OKGREEN}[0]{Colors.ENDC} None of the above (skip MAL matching)")
    print_separator()
    
    while True:
        try:
            choice = input(f"{Colors.BOLD}Select the correct anime [0-{len(display_animes)}]: {Colors.ENDC}").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                print_status("Skipping MAL matching", "warning")
                return None
            
            if 1 <= choice_num <= len(display_animes):
                selected = display_animes[choice_num - 1]
                print_status(f"Selected: {_get_best_title(selected)}", "success")
                return selected
            else:
                print_status(f"Please enter a number between 0 and {len(display_animes)}", "error")
        except ValueError:
            print_status("Please enter a valid number", "error")
        except KeyboardInterrupt:
            print_status("\nSkipping MAL matching", "warning")
            return None


def search_anime_on_mal(anime_name: str, interactive: bool = True) -> dict | None:
    """Recherche un anime sur MyAnimeList via l'API Jikan"""
    # Vérifier le cache d'abord
    cache_key = anime_name.lower().strip()
    if cache_key in _mal_search_cache:
        print_status(f"Using cached MAL data for: {anime_name}", "info")
        return _mal_search_cache[cache_key]
    
    # Nettoyer le nom avant la recherche
    cleaned_name = _clean_anime_name(anime_name)
    
    # Tenter plusieurs variations du nom
    search_queries = [cleaned_name]
    
    # Si le nom nettoyé est différent, ajouter aussi l'original
    if cleaned_name != anime_name:
        search_queries.append(anime_name)
    
    print_status(f"Searching MAL for: {cleaned_name}", "info")
    
    all_results = []
    
    for query in search_queries:
        try:
            i = 0
            while True:
                response = httpx.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=20", timeout=15.0)
                i += 1
                if response.status_code != 429 or i > 9:
                    break

            response.raise_for_status()
            animes = response.json().get("data", [])

            if not animes:
                continue

            # Ajouter tous les résultats uniques
            for anime in animes:
                if anime not in all_results:
                    all_results.append(anime)

        except httpx.HTTPStatusError as e:
            print_status(f"Error fetching data from Jikan API: {str(e)}", "warning")
            continue
        except Exception as e:
            print_status(f"Unexpected error while searching MAL: {str(e)}", "warning")
            continue
    
    if not all_results:
        print_status(f"No results found for '{anime_name}'", "warning")
        _mal_search_cache[cache_key] = None
        return None
    
    # Séparer les résultats en séries et films
    tv_series = []
    other_types = []
    
    for anime in all_results:
        anime_type = anime.get("type", "").lower()
        if anime_type in ["tv", "ona"]:
            tv_series.append(anime)
        else:
            other_types.append(anime)
    
    # Chercher une correspondance exacte dans tous les titres
    for query in search_queries:
        name_normalized = normalize(query)
        
        # D'abord dans les séries TV
        for anime in tv_series:
            for title in anime.get("titles", []):
                title_normalized = normalize(title.get("title", ""))
                if name_normalized == title_normalized:
                    print_status(f"Found exact match: {_get_best_title(anime)}", "success")
                    result = {
                        "mal_id": anime.get("mal_id"),
                        "title": _get_best_title(anime),
                        "type": anime.get("type")
                    }
                    _mal_search_cache[cache_key] = result
                    return result
        
        # Puis dans les autres types
        for anime in other_types:
            for title in anime.get("titles", []):
                title_normalized = normalize(title.get("title", ""))
                if name_normalized == title_normalized:
                    print_status(f"Found exact match: {_get_best_title(anime)}", "success")
                    result = {
                        "mal_id": anime.get("mal_id"),
                        "title": _get_best_title(anime),
                        "type": anime.get("type")
                    }
                    _mal_search_cache[cache_key] = result
                    return result
    
    # Pas de correspondance exacte, proposer à l'utilisateur
    if interactive:
        # Filtrer les films si on ne cherche pas explicitement un film
        candidates = tv_series if tv_series and not _is_movie_title(anime_name) else all_results
        
        selected = _display_search_results(candidates, anime_name)
        
        if selected:
            result = {
                "mal_id": selected.get("mal_id"),
                "title": _get_best_title(selected),
                "type": selected.get("type")
            }
            _mal_search_cache[cache_key] = result
            return result
        else:
            _mal_search_cache[cache_key] = None
            return None
    else:
        # Mode non-interactif : retourner le premier résultat TV ou le premier tout court
        if tv_series and not _is_movie_title(anime_name):
            first_anime = tv_series[0]
        elif all_results:
            first_anime = all_results[0]
        else:
            _mal_search_cache[cache_key] = None
            return None
        
        print_status(f"Using first result: {_get_best_title(first_anime)}", "info")
        result = {
            "mal_id": first_anime.get("mal_id"),
            "title": _get_best_title(first_anime),
            "type": first_anime.get("type")
        }
        _mal_search_cache[cache_key] = result
        return result


def create_match_file(save_dir: str, anime_name: str, interactive: bool = True) -> None:
    """Crée le fichier .match avec les informations MAL"""
    # Utiliser un verrou pour éviter les appels simultanés
    with _cache_lock:
        try:
            match_file_path = os.path.join(save_dir, '.match')
            cache_key = anime_name.lower().strip()
            
            # Vérifier le cache d'abord (peut avoir été rempli par un autre thread)
            if cache_key in _mal_search_cache:
                print_status(f"Using cached MAL data (already in memory)", "info")
                return
            
            # Vérifier si le fichier existe déjà
            if os.path.exists(match_file_path):
                print_status(f"Match file already exists: {match_file_path}", "info")
                
                # IMPORTANT : Charger les données du fichier dans le cache
                try:
                    with open(match_file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        mal_id = None
                        title = None
                        for line in lines:
                            if line.startswith('mal-id:'):
                                mal_id_str = line.split(':', 1)[1].strip()
                                if mal_id_str != 'unknown':
                                    mal_id = int(mal_id_str)
                            elif line.startswith('title:'):
                                title = line.split(':', 1)[1].strip()
                        
                        if mal_id and title:
                            _mal_search_cache[cache_key] = {
                                "mal_id": mal_id,
                                "title": title,
                                "type": "TV"
                            }
                            print_status(f"Loaded MAL data from existing file into cache", "info")
                        else:
                            _mal_search_cache[cache_key] = None
                except Exception as e:
                    print_status(f"Could not read existing match file: {e}", "warning")
                    _mal_search_cache[cache_key] = None
                
                return
            
            print_separator()
            print(f"{Colors.BOLD}{Colors.HEADER}🔍 Searching for anime on MyAnimeList...{Colors.ENDC}")
            print_separator()
            
            # Rechercher l'anime sur MAL
            mal_data = search_anime_on_mal(anime_name, interactive=interactive)
            
            if mal_data:
                with open(match_file_path, 'w', encoding='utf-8') as match_file:
                    match_file.write(f"title: {mal_data['title']}\n")
                    match_file.write(f"mal-id: {mal_data['mal_id']}\n")
                
                print_separator()
                print_status(f"✓ Match file created: {match_file_path}", "success")
                print_status(f"  → Title: {mal_data['title']}", "info")
                print_status(f"  → MAL ID: {mal_data['mal_id']}", "info")
                print_status(f"  → Type: {mal_data['type']}", "info")
                print_separator()
            else:
                # Créer le fichier avec des valeurs par défaut si rien n'est trouvé
                with open(match_file_path, 'w', encoding='utf-8') as match_file:
                    match_file.write(f"title: {anime_name}\n")
                    match_file.write("mal-id: unknown\n")
                
                print_separator()
                print_status(f"Match file created with default values: {match_file_path}", "warning")
                print_status(f"Could not find or match anime on MAL", "warning")
                print_separator()
                
        except Exception as e:
            print_status(f"Error creating match file: {str(e)}", "error")
# ==================== FIN DES NOUVELLES FONCTIONNALITÉS ====================


def download_episode(episode_num, url, video_source, anime_name, save_dir, use_ts_threading=False, automatic_mp4=False, pre_selected_tool=None):
    if not video_source:
        print_status(f"Could not extract video source for episode {episode_num}", "error")
        return False, None
    
    print_separator()
    print_status(f"Processing episode: {episode_num}", "info")
    print_status(f"Source: {url[:60]}...", "info")
    
    # ==================== AJOUT : Dossier Saison 01 + fichier .match ====================
    # Créer le dossier de saison
    season_dir = os.path.join(save_dir, "Saison 01")
    os.makedirs(season_dir, exist_ok=True)
    
    # Créer le fichier .match (une seule fois grâce au cache)
    create_match_file(season_dir, anime_name)
    
    # Modifier le chemin de sauvegarde pour inclure le dossier de saison
    save_path = os.path.join(season_dir, f"{anime_name}_episode_{episode_num}.mp4")
    # ==================== FIN AJOUT ====================
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}⬇️ DOWNLOADING EPISODE {episode_num}{Colors.ENDC}")
    print_separator()
    
    try:
        success, output_path = download_video(video_source, save_path, use_ts_threading=use_ts_threading, url=url, automatic_mp4=automatic_mp4)
    except Exception as e:
        print_status(f"Download failed for episode {episode_num}: {str(e)}", "error")
        return False, None
    
    if not success:
        print_status(f"Failed to download episode {episode_num}", "error")
        return False, None
    
    print_separator()
    
    if 'm3u8' in video_source and output_path.endswith('.ts'):
        print_status(f"Video saved as {output_path} (MPEG-TS format, playable in VLC or similar players)", "success")
        if automatic_mp4:
            success, final_path = convert_ts_to_mp4(output_path, save_path, pre_selected_tool)
            if success:
                print_status(f"Episode {episode_num} successfully saved to: {final_path}", "success")
                try:
                    os.remove(output_path)
                    print_status(f"Removed temporary .ts file: {output_path}", "info")
                except Exception as e:
                    print_status(f"Could not remove temporary .ts file: {str(e)}", "warning")
                return True, final_path
            else:
                print_status(f"Conversion failed for episode {episode_num}, keeping .ts file: {output_path}", "error")
                return False, output_path
        else:
            print_status(f"Keeping .ts file for episode {episode_num}: {output_path}", "info")
            return True, output_path
    else:
        print_status(f"Episode {episode_num} successfully saved to: {save_path}", "success")
        return True, save_path
