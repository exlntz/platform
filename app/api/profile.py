from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException,status
from app.core.database import SessionDep
from app.core.dependencies import UserDep
from app.schemas.user import UserStatsResponse,UserProfileRead
import uuid
from app.schemas.user import EloHistoryPoint
from app.utils.achievments import check_and_award_achievement
import os
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from app.services.user_stats import calculate_user_stats, calculate_elo_history
from app.services.user_stats import calculate_profile_info

IS_PROD = os.getenv('VITE_IS_PROD') == 'true'

router = APIRouter(prefix='/profile',tags=['Профиль'])

@router.get('/',summary='Профиль пользователя',description='Возвращает данные пользователя и его статистику в одном структурированном ответе.')
async def get_my_profile(
        session: SessionDep,
        current_user: UserDep
) -> UserProfileRead:

    return await calculate_profile_info(session, current_user.id)


register_heif_opener()
ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'heic', 'heif'}

@router.post('/avatar', summary='Загрузить аватарку')
async def upload_avatar(
        session: SessionDep,
        current_user: UserDep,
        file: UploadFile = File(...)
):

    filename = file.filename or ""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ""

    if not ext and file.content_type:
        ctype = file.content_type.split('/')[-1].lower()
        if 'heic' in ctype or 'heif' in ctype:
            ext = 'heic'
        elif ctype == 'octet-stream' and filename.lower().endswith('.heic'):
            ext = 'heic'

    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Формат {ext} не поддерживается. Разрешены: {", ".join(ALLOWED_AVATAR_EXTENSIONS)}'
        )

    if current_user.avatar_url:
        old_path = current_user.avatar_url.replace('/api/', '').lstrip('/')
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                print(f"Ошибка удаления старого файла: {e}")

    ext = 'jpg'

    file_name = f"user_{current_user.id}_{uuid.uuid4().hex}.{ext}"
    base_dir = Path(__file__).resolve().parent.parent.parent
    static_dir = base_dir / "static" / "avatars"
    static_dir.mkdir(parents=True, exist_ok=True)
    file_disk_path = static_dir / file_name

    try:
        image = Image.open(file.file)

        image = ImageOps.exif_transpose(image)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.save(file_disk_path, "JPEG", quality=85)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки изображения: {e}")

    prefix = "/api" if IS_PROD else ""
    generated_url = f"{prefix}/static/avatars/{file_name}"

    current_user.avatar_url = generated_url
    session.add(current_user)

    new_badges = await check_and_award_achievement(current_user, session)
    await session.commit()

    return {
        'url': generated_url,
        'new_achievements': new_badges,
    }


@router.get('/stats', summary='Детальная статистика по предметам')
async def get_user_stats(
        current_user: UserDep,
        session: SessionDep,
) -> UserStatsResponse:

    return await calculate_user_stats(session, current_user.id)


@router.get('/elo_history',summary='История рейтинга для графика в профиле')
async def get_elo_history(
    session: SessionDep,
    current_user: UserDep,
    limit: int = 50
) -> list[EloHistoryPoint]:

    return await calculate_elo_history(session, current_user.id,limit)