from functools import wraps

from src.cache import redis_client


def agent_state_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_id = kwargs.get("session_id")
        if session_id is None:
            # Có thể lấy từ args nếu hàm nhận theo thứ tự, ví dụ def foo(session_id, ...)
            # session_id = args[0] nếu đảm bảo vị trí
            raise ValueError("session_id is required in kwargs")

        cache_key = f"ai_agent:{session_id}"
        cached_agent_state = redis_client.get(cache_key)

        # Truyền cached_agent_state về cho func, các tham số khác giữ nguyên
        result = func(cached_agent_state, *args, **kwargs)

        # Cache lại state mới nếu result hợp lệ
        if hasattr(result, "model_dump_json"):
            redis_client.setex(cache_key, 600, result.model_dump_json())

        return result

    return wrapper
