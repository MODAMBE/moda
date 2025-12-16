from celery import shared_task
from .models import Video

@shared_task
def transcode_video(video_id):
    """
    Exemple simple de tâche Celery.
    Tu remplaceras par ton vrai transcodage.
    """
    try:
        video = Video.objects.get(id=video_id)
        print(f"Transcodage de la vidéo {video.id} : OK")
        # traitement réel ici...
        
    except Video.DoesNotExist:
        print("Vidéo introuvable")
from celery import shared_task
from .models import Video
import subprocess
from django.conf import settings
from pathlib import Path
from PIL import Image

@shared_task
def transcode_video(video_id):
    v = Video.objects.get(id=video_id)
    input_path = v.video_file.path
    base = Path(input_path).parent
    # génère miniature (1ère frame)
    thumb_path = base / f"thumb_{v.id}.jpg"
    try:
        # extraire image
        subprocess.run([
            "ffmpeg", "-y", "-i", str(input_path),
            "-ss", "00:00:01.000", "-vframes", "1", str(thumb_path)
        ], check=True)
        # sauvegarder thumbnail
        v.thumbnail.save(f"thumb_{v.id}.jpg", open(str(thumb_path), "rb"))
    except Exception as e:
        print("thumbnail error", e)

    # Pour HLS tu pourrais lancer ffmpeg pour générer master.m3u8 et stocker URL dans v.hls_playlist
    # Simplification: on laisse video_file et on rend lecture dans <video> direct (fallback).
    v.save()
    return True
