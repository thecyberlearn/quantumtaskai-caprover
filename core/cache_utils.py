"""
Cache utilities for performance optimization.
"""

from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def cache_user_data(cache_key_prefix, timeout=None):
    """
    Decorator for caching user-specific data.
    
    Args:
        cache_key_prefix (str): Prefix for the cache key
        timeout (int): Cache timeout in seconds (None for default)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                # Don't cache for anonymous users
                return func(request, *args, **kwargs)
            
            # Create unique cache key
            cache_key = f"{cache_key_prefix}_{request.user.id}"
            if args or kwargs:
                # Include args and kwargs in cache key for uniqueness
                key_data = f"{args}_{kwargs}"
                key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
                cache_key += f"_{key_hash}"
            
            try:
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed for {cache_key}: {e}")
            
            # Execute function and cache result
            result = func(request, *args, **kwargs)
            
            try:
                # Determine cache timeout
                if timeout is None:
                    cache_timeout = 300 if settings.DEBUG else 1800  # 5 min / 30 min
                else:
                    cache_timeout = timeout
                
                cache.set(cache_key, result, cache_timeout)
                logger.debug(f"Cached result for {cache_key} (timeout: {cache_timeout}s)")
            except Exception as e:
                logger.warning(f"Cache set failed for {cache_key}: {e}")
            
            return result
        return wrapper
    return decorator


def cache_expensive_query(cache_key, timeout=None):
    """
    Decorator for caching expensive database queries.
    
    Args:
        cache_key (str): Cache key for the query
        timeout (int): Cache timeout in seconds (None for default)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create unique cache key with function args
            full_cache_key = cache_key
            if args or kwargs:
                key_data = f"{args}_{kwargs}"
                key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
                full_cache_key += f"_{key_hash}"
            
            try:
                # Try to get from cache
                cached_result = cache.get(full_cache_key)
                if cached_result is not None:
                    logger.debug(f"Query cache hit for {full_cache_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Query cache get failed for {full_cache_key}: {e}")
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            try:
                # Determine cache timeout
                if timeout is None:
                    cache_timeout = 600 if settings.DEBUG else 3600  # 10 min / 1 hour
                else:
                    cache_timeout = timeout
                
                cache.set(full_cache_key, result, cache_timeout)
                logger.debug(f"Cached query result for {full_cache_key} (timeout: {cache_timeout}s)")
            except Exception as e:
                logger.warning(f"Query cache set failed for {full_cache_key}: {e}")
            
            return result
        return wrapper
    return decorator


def invalidate_user_cache(user_id, cache_key_prefix):
    """
    Invalidate all cache entries for a specific user and prefix.
    
    Args:
        user_id (int): User ID
        cache_key_prefix (str): Cache key prefix to invalidate
    """
    try:
        # Create pattern for user-specific cache keys
        cache_pattern = f"{cache_key_prefix}_{user_id}"
        
        # Note: This is a simplified implementation
        # In production, you might want to use Redis pattern matching
        # or maintain a list of cache keys to invalidate
        
        # For now, we'll invalidate common variations
        cache_keys_to_invalidate = [
            f"{cache_pattern}",
            f"{cache_pattern}_*",  # This won't work with default cache, needs Redis
        ]
        
        for key in cache_keys_to_invalidate:
            cache.delete(key)
        
        logger.info(f"Invalidated cache for user {user_id} with prefix {cache_key_prefix}")
    except Exception as e:
        logger.warning(f"Cache invalidation failed for user {user_id}: {e}")


def get_cache_stats():
    """
    Get cache statistics (Redis only).
    Returns dict with cache statistics or None if not available.
    """
    try:
        # This only works with Redis backend
        if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
            redis_client = cache._cache.get_client()
            info = redis_client.info('memory')
            return {
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'used_memory_peak': info.get('used_memory_peak', 0),
                'used_memory_peak_human': info.get('used_memory_peak_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
            }
    except Exception as e:
        logger.debug(f"Could not get cache stats: {e}")
    
    return None