import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

from src.gui.utils.cloudflare import get_headers
from src.gui.utils.error import DownloadError, FetchError
from src.gui.utils.utils import order_episodes_sources
from src.utils.download.download_video import download_video
from src.utils.fetch.fetch_episodes import fetch_episodes
from src.utils.fetch.fetch_video_source import fetch_video_source
from src.utils.get.get_save_directory import format_save_path
from src.utils.ts.convert_ts_to_mp4 import convert_ts_to_mp4


def _extract_episode_sources_from_data(episode_data: dict[str, list[str]], episode_num: int):
    sources = []
    for season_sources in episode_data.values():
        if len(season_sources) >= episode_num:
            sources.append(season_sources[episode_num - 1])
    return sources


def _extract_name_and_season_from_url(url: str) -> tuple[str, str]:
    splitted_url = url.split("/")
    offset = 1 if splitted_url[-1] == '' else 0
    season = splitted_url[-2 - offset]
    anime_name = splitted_url[-3 - offset]
    return anime_name, season


def download_episodes_from_url(season_url: str, episode_to_download: Iterable[int], download_all: bool,
                               use_threading: bool, automatic_mp4: bool, pre_selected_tool: str="ffmpeg"):
    anime_name, season = _extract_name_and_season_from_url(season_url)
    output_path = format_save_path(anime_name, season)

    episodes_data = fetch_episodes(season_url, headers=get_headers())
    if not episodes_data:
        raise FetchError(f"Failed to fetch episodes for {anime_name} from {season_url}")

    downloading_errors = []

    if download_all:
        episode_amount = max(len(sources) for sources in episodes_data.values()) if episodes_data else 0
        episode_to_download = range(1, episode_amount + 1)

    def process_episode(episode_num_to_process):
        episode_sources = _extract_episode_sources_from_data(episodes_data, episode_num_to_process)
        if not episode_sources:
            raise FetchError(f"Failed to fetch episode sources for {anime_name} - {season} - Episode {episode_num_to_process}")

        episode_sources = order_episodes_sources(episode_sources)
        download_episode_from_sources(
            episode_num_to_process,
            episode_sources,
            anime_name,
            output_path,
            use_threading,
            automatic_mp4,
            pre_selected_tool
        )

    if use_threading and episode_to_download:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_episode, ep_num): ep_num for ep_num in episode_to_download}

            for future in as_completed(futures):
                try:
                    future.result()
                except (DownloadError, FetchError) as e:
                    downloading_errors.append(e)
                except Exception as e:
                    downloading_errors.append(DownloadError(f"Unexpected error on episode: {e}"))
    else:
        for episode_num in episode_to_download:
            try:
                process_episode(episode_num)
            except DownloadError as e:
                downloading_errors.append(e)

    if downloading_errors:
        raise DownloadError(
            f"Failed to download all episodes of {anime_name}.\nErrors: {', '.join(str(e) for e in downloading_errors)}")


def download_episode_from_sources(episode_num: int, video_sources: list[str], anime_name: str, save_dir: str, use_threading: bool, automatic_mp4: bool, pre_selected_tool="ffmpeg"):
    success = False
    i = 0
    while not success and i < len(video_sources):
        video_source = video_sources[i]
        success, _ = download_episode_from_source(episode_num, video_source, anime_name, save_dir, use_threading,
                                                  automatic_mp4, pre_selected_tool)
        i += 1

    if not success:
        raise DownloadError(f"Failed to download episode {episode_num} of {anime_name} from sources.")


def download_episode_from_source(episode_num: int, url: str, anime_name: str, save_dir: str, use_ts_threading: bool, automatic_mp4: bool, pre_selected_tool="ffmpeg"):
    season_dir = save_dir
    os.makedirs(season_dir, exist_ok=True)

    video_source = fetch_video_source(url)

    save_path = os.path.join(season_dir, f"{anime_name if anime_name else 'episode'}_{episode_num}.mp4")

    try:
        success, output_path = download_video(video_source, save_path, use_ts_threading=use_ts_threading, url=url,
                                              automatic_mp4=True, interactive=True)
    except Exception as e:
        raise ValueError(f"Failed to download video : {e}")

    if not success:
        return False, None

    can_be_converted = 'm3u8' in video_source and output_path.endswith('.ts')
    if not can_be_converted:
        return True, save_path

    if not automatic_mp4:
        return True, output_path

    success, final_path = convert_ts_to_mp4(output_path, save_path, pre_selected_tool)
    if success:
        os.remove(output_path)
        return True, final_path
    return False, output_path
