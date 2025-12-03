"""ユーザー設定API (LLM Config, API Keys)."""

import hashlib
import secrets
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import UserApiKeyRepository, UserLLMConfigRepository
from ...services.vault_service import get_vault_service
from ..deps import get_current_user_id, get_db, get_user_api_key_repo, get_user_llm_config_repo

router = APIRouter()


# =============================================================================
# LLM Config Pydantic Models
# =============================================================================


class UserLLMConfigCreate(BaseModel):
    """LLM Config作成リクエスト."""

    provider: str  # 'openai', 'anthropic', 'google', 'bedrock'
    api_key: str  # 生のAPIキー（暗号化して保存）
    is_default: bool = False


class UserLLMConfigResponse(BaseModel):
    """LLM Configレスポンス."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    provider: str
    is_default: bool
    created_at: datetime


# =============================================================================
# API Key Pydantic Models
# =============================================================================


class UserApiKeyCreate(BaseModel):
    """API Key作成リクエスト."""

    name: str
    scopes: list[str] = []  # ['agents:read', 'agents:execute']
    rate_limit: int = 1000
    expires_at: datetime | None = None


class UserApiKeyResponse(BaseModel):
    """API Keyレスポンス（一覧表示用、生キーなし）."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    key_prefix: str
    scopes: list[str]
    rate_limit: int
    expires_at: datetime | None
    last_used_at: datetime | None
    created_at: datetime


class UserApiKeyCreated(BaseModel):
    """API Key作成レスポンス（生キー含む、作成時のみ）."""

    id: UUID
    name: str
    key: str  # 生キー（この1回のみ表示）
    key_prefix: str
    scopes: list[str]
    rate_limit: int
    expires_at: datetime | None
    created_at: datetime


# =============================================================================
# LLM Config Endpoints
# =============================================================================


@router.get("/llm-configs", response_model=list[UserLLMConfigResponse])
async def list_llm_configs(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: UserLLMConfigRepository = Depends(get_user_llm_config_repo),
) -> list[UserLLMConfigResponse]:
    """LLM Config一覧取得."""
    configs = await repo.list_by_user(db, user_id)
    return [UserLLMConfigResponse.model_validate(config) for config in configs]


@router.post(
    "/llm-configs", response_model=UserLLMConfigResponse, status_code=status.HTTP_201_CREATED
)
async def create_llm_config(
    config_data: UserLLMConfigCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: UserLLMConfigRepository = Depends(get_user_llm_config_repo),
) -> UserLLMConfigResponse:
    """LLM Config作成."""
    # 既存の同一プロバイダー設定がないか確認
    existing = await repo.get_by_user_provider(db, user_id, config_data.provider)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"LLM config for provider '{config_data.provider}' already exists",
        )

    # APIキーをVaultに保存
    vault = get_vault_service()
    vault_secret_id = await vault.store_secret(user_id, config_data.provider, config_data.api_key)

    # Config作成
    config = await repo.create(
        db,
        user_id=user_id,
        provider=config_data.provider,
        vault_secret_id=vault_secret_id,
        is_default=config_data.is_default,
    )
    return UserLLMConfigResponse.model_validate(config)


@router.delete("/llm-configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_llm_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: UserLLMConfigRepository = Depends(get_user_llm_config_repo),
) -> None:
    """LLM Config削除."""
    config = await repo.get_by_user(db, config_id, user_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LLM config {config_id} not found",
        )

    # Vaultからシークレット削除
    vault = get_vault_service()
    await vault.delete_secret(config.vault_secret_id)

    await repo.delete(db, config)


# =============================================================================
# API Key Endpoints
# =============================================================================


def _generate_api_key() -> tuple[str, str, str]:
    """Generate a new API key.

    Returns:
        tuple: (full_key, key_hash, key_prefix)
    """
    # ランダムキー生成 (24 bytes = 192 bits, base64で32文字)
    key_suffix = secrets.token_urlsafe(24)

    # プレフィックス付きキー
    full_key = f"sk_live_{key_suffix}"

    # SHA-256ハッシュ
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()

    # 表示用プレフィックス
    key_prefix = f"sk_live_{key_suffix[:4]}..."

    return full_key, key_hash, key_prefix


@router.get("/api-keys", response_model=list[UserApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: UserApiKeyRepository = Depends(get_user_api_key_repo),
) -> list[UserApiKeyResponse]:
    """API Key一覧取得."""
    keys = await repo.list_by_user(db, user_id)
    return [UserApiKeyResponse.model_validate(key) for key in keys]


@router.post("/api-keys", response_model=UserApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: UserApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: UserApiKeyRepository = Depends(get_user_api_key_repo),
) -> UserApiKeyCreated:
    """API Key作成.

    注意: 生のAPIキーはこのレスポンスでのみ返されます。
    以降は表示できないため、ユーザーに保存を促してください。
    """
    # キー生成
    full_key, key_hash, key_prefix = _generate_api_key()

    # DB保存
    api_key = await repo.create(
        db,
        user_id=user_id,
        name=key_data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=key_data.scopes,
        rate_limit=key_data.rate_limit,
        expires_at=key_data.expires_at,
    )

    return UserApiKeyCreated(
        id=api_key.id,
        name=api_key.name,
        key=full_key,  # 生キー（この1回のみ）
        key_prefix=key_prefix,
        scopes=api_key.scopes,
        rate_limit=api_key.rate_limit,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
    )


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: UserApiKeyRepository = Depends(get_user_api_key_repo),
) -> None:
    """API Key削除."""
    api_key = await repo.get_by_user(db, key_id, user_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key {key_id} not found",
        )
    await repo.delete(db, api_key)
