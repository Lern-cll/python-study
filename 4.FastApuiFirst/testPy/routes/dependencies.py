"""依赖注入示例：公共参数、依赖函数、可复用子依赖。

FastAPI 的依赖通过 `Depends(...)` 注入到路由处理函数中，
可统一在此处声明，路由文件只需 `from .dependencies import ...` 使用。
"""
from fastapi import Depends, Header, HTTPException, Query


# ---------- 公共参数：分页 ----------
class Pagination:
    """分页参数依赖：统一处理 page/size。"""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码，从 1 开始"),
        size: int = Query(10, ge=1, le=100, description="每页条数，最大 100"),
    ) -> None:
        self.page = page
        self.size = size
        self.offset = (page - 1) * size

    def __repr__(self) -> str:
        return f"Pagination(page={self.page}, size={self.size})"


# ---------- 依赖函数：请求头鉴权 ----------
def require_token(x_token: str = Header(..., description="访问令牌")) -> str:
    """校验自定义请求头 X-Token。"""
    if x_token != "demo-token":
        raise HTTPException(status_code=401, detail="无效的 X-Token")
    return x_token


# ---------- 子依赖：组合多个依赖 ----------
def get_current_user(
    token: str = Depends(require_token),
    user_id: int = Query(..., description="用户 ID"),
) -> dict:
    """组合鉴权 + 查询参数，返回当前用户信息。"""
    return {"user_id": user_id, "token": token}


__all__ = [
    "Pagination",
    "require_token",
    "get_current_user",
]
