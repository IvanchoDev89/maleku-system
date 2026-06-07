"""
Token Blacklist Service
Manages revoked JWT tokens using Redis for instant invalidation
"""
from datetime import datetime, timezone
import hashlib
import redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TokenBlacklist:
    """Service for blacklisting JWT tokens"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
        
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                self.enabled = True
                logger.info("Token blacklist (Redis) connected")
            except (OSError, ConnectionError, redis.RedisError) as e:
                logger.error(f"Failed to connect to Redis for token blacklist: {e}")
    
    def _hash_token(self, token: str) -> str:
        """Generate SHA-256 hash of token for secure storage"""
        return hashlib.sha256(token.encode()).hexdigest()[:32]
    
    def blacklist_token(self, token: str, expires_at: datetime) -> bool:
        """
        Add a token to the blacklist.
        
        Args:
            token: The JWT token to blacklist (or its jti claim)
            expires_at: When the token naturally expires
            
        Returns:
            True if successfully blacklisted
        """
        if not self.enabled or not self.redis_client:
            logger.warning("Token blacklist not available - token not revoked")
            return False
        
        try:
            # Calculate TTL (time until token expires)
            now = datetime.now(timezone.utc)
            ttl = int((expires_at - now).total_seconds())
            
            if ttl > 0:
                # Store token hash (not the full token) with TTL for security
                token_hash = self._hash_token(token)
                self.redis_client.setex(
                    f"blacklist:token:{token_hash}",
                    ttl,
                    "revoked"
                )
                logger.info("Token added to blacklist")
                return True
            else:
                # Token already expired, no need to blacklist
                return True
                
        except redis.RedisError as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
        except (OSError, RuntimeError) as e:
            logger.critical(f"Unexpected error blacklisting token: {e}")
            raise
    
    def is_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token: The JWT token to check
            
        Returns:
            True if token is blacklisted/revoked
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            token_hash = self._hash_token(token)
            return self.redis_client.exists(f"blacklist:token:{token_hash}") > 0
        except redis.RedisError as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False
        except (OSError, RuntimeError) as e:
            logger.critical(f"Unexpected error checking blacklist: {e}")
            raise
    
    def blacklist_user_tokens(self, user_id: str, expire_all_after: datetime) -> bool:
        """
        Blacklist all tokens for a user (useful on password change/logout all sessions).
        
        Args:
            user_id: The user ID
            expire_all_after: Blacklist all tokens issued before this time
            
        Returns:
            True if successful
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            # Store timestamp - any token issued before this is invalid
            self.redis_client.set(
                f"blacklist:user:{user_id}",
                expire_all_after.isoformat()
            )
            logger.info(f"All tokens blacklisted for user {user_id}")
            return True
        except redis.RedisError as e:
            logger.error(f"Failed to blacklist user tokens: {e}")
            return False
        except (OSError, RuntimeError) as e:
            logger.critical(f"Unexpected error blacklisting user tokens: {e}")
            raise
    
    def is_user_tokens_blacklisted(self, user_id: str, token_issued_at: datetime) -> bool:
        """
        Check if user's tokens are blacklisted and if this specific token is affected.
        
        Args:
            user_id: The user ID
            token_issued_at: When this token was issued
            
        Returns:
            True if this token should be rejected
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            blacklist_time = self.redis_client.get(f"blacklist:user:{user_id}")
            if blacklist_time:
                from datetime import datetime
                blacklist_dt = datetime.fromisoformat(blacklist_time)
                return token_issued_at < blacklist_dt
            return False
        except redis.RedisError as e:
            logger.error(f"Failed to check user token blacklist: {e}")
            return False
        except (OSError, RuntimeError) as e:
            logger.critical(f"Unexpected error checking user blacklist: {e}")
            raise


# Singleton instance
token_blacklist = TokenBlacklist()
