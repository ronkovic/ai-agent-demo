"""Vault service for secure secret storage.

本番環境: Supabase Vault
開発環境: Fernet暗号化 + DB保存
"""

import base64
import hashlib
import json
from uuid import UUID

import httpx
from cryptography.fernet import Fernet

from ..core.config import settings


class VaultService:
    """LLM APIキーの暗号化保存サービス.

    本番環境ではSupabase Vaultを使用し、
    開発環境ではFernet暗号化でDB内に保存します。
    """

    def __init__(self) -> None:
        """Initialize vault service."""
        self.use_supabase = bool(settings.supabase_url and settings.supabase_service_role_key)
        self._fernet: Fernet | None = None

        if not self.use_supabase:
            # 開発用Fernet暗号化キーを取得または生成
            key = self._get_or_generate_encryption_key()
            self._fernet = Fernet(key)

    def _get_or_generate_encryption_key(self) -> bytes:
        """Get or generate Fernet encryption key."""
        if settings.encryption_key:
            # 環境変数から取得
            return settings.encryption_key.encode()

        # 固定キーを生成（開発環境用、DATABASE_URLをシードとして使用）
        seed = settings.database_url or "dev-seed-key"
        key_bytes = hashlib.sha256(seed.encode()).digest()
        return base64.urlsafe_b64encode(key_bytes)

    async def store_secret(self, user_id: UUID, provider: str, api_key: str) -> str:
        """Store API key securely.

        Args:
            user_id: User ID
            provider: LLM provider name
            api_key: API key to store

        Returns:
            Secret ID for later retrieval
        """
        if self.use_supabase:
            return await self._store_supabase(user_id, provider, api_key)
        else:
            return self._store_local(user_id, provider, api_key)

    async def retrieve_secret(self, secret_id: str) -> str:
        """Retrieve API key by secret ID.

        Args:
            secret_id: Secret ID returned from store_secret

        Returns:
            Decrypted API key
        """
        if self.use_supabase:
            return await self._retrieve_supabase(secret_id)
        else:
            return self._retrieve_local(secret_id)

    async def delete_secret(self, secret_id: str) -> None:
        """Delete a secret.

        Args:
            secret_id: Secret ID to delete
        """
        if self.use_supabase:
            await self._delete_supabase(secret_id)
        # ローカルモードでは特に削除処理は不要（secret_idはDB参照のみ）

    # =========================================================================
    # Supabase Vault implementation
    # =========================================================================

    async def _store_supabase(self, user_id: UUID, provider: str, api_key: str) -> str:
        """Store secret in Supabase Vault."""
        secret_name = f"llm_key_{user_id}_{provider}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.supabase_url}/rest/v1/rpc/vault_insert_secret",
                headers={
                    "apikey": settings.supabase_service_role_key,
                    "Authorization": f"Bearer {settings.supabase_service_role_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "new_secret": api_key,
                    "new_name": secret_name,
                },
            )

            if response.status_code != 200:
                raise RuntimeError(f"Failed to store secret in Vault: {response.text}")

            # Vault returns the secret ID
            secret_id = response.json()
            return str(secret_id)

    async def _retrieve_supabase(self, secret_id: str) -> str:
        """Retrieve secret from Supabase Vault."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.supabase_url}/rest/v1/rpc/vault_read_secret",
                headers={
                    "apikey": settings.supabase_service_role_key,
                    "Authorization": f"Bearer {settings.supabase_service_role_key}",
                    "Content-Type": "application/json",
                },
                json={"secret_id": secret_id},
            )

            if response.status_code != 200:
                raise RuntimeError(f"Failed to retrieve secret from Vault: {response.text}")

            return response.json()

    async def _delete_supabase(self, secret_id: str) -> None:
        """Delete secret from Supabase Vault."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.supabase_url}/rest/v1/rpc/vault_delete_secret",
                headers={
                    "apikey": settings.supabase_service_role_key,
                    "Authorization": f"Bearer {settings.supabase_service_role_key}",
                    "Content-Type": "application/json",
                },
                json={"secret_id": secret_id},
            )

            if response.status_code != 200:
                raise RuntimeError(f"Failed to delete secret from Vault: {response.text}")

    # =========================================================================
    # Local Fernet implementation (development)
    # =========================================================================

    def _store_local(self, user_id: UUID, provider: str, api_key: str) -> str:
        """Store secret locally using Fernet encryption.

        暗号化されたAPIキーをsecret_idとして返します。
        実際のAPIキーはDBのvault_secret_idフィールドに暗号化状態で保存されます。
        """
        if not self._fernet:
            raise RuntimeError("Fernet encryption not initialized")

        # APIキーを暗号化
        encrypted = self._fernet.encrypt(api_key.encode())

        # メタデータを含めてエンコード
        data = {
            "user_id": str(user_id),
            "provider": provider,
            "encrypted_key": encrypted.decode(),
        }
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

    def _retrieve_local(self, secret_id: str) -> str:
        """Retrieve secret from local encrypted storage."""
        if not self._fernet:
            raise RuntimeError("Fernet encryption not initialized")

        try:
            # secret_idをデコード
            data = json.loads(base64.urlsafe_b64decode(secret_id.encode()))
            encrypted_key = data["encrypted_key"].encode()

            # 復号
            return self._fernet.decrypt(encrypted_key).decode()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve secret: {e}") from e


# シングルトンインスタンス
_vault_service: VaultService | None = None


def get_vault_service() -> VaultService:
    """Get vault service singleton instance."""
    global _vault_service
    if _vault_service is None:
        _vault_service = VaultService()
    return _vault_service
