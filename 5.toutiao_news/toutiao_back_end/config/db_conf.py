from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# news_app 数据库连接字符串
# 平台： MYSQL80   账号： root   密码： Lern@185
# 注意：密码里的 @ 必须 URL 编码为 %40，否则 SQLAlchemy 解析 URL 时会出错
ASYNC_DATABASE_URL = "mysql+aiomysql://root:Lern%40185@localhost:3306/news_app?charset=utf8mb4"

# 1.创建异步数据库引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,          # 可选:输出SQL日志
    pool_size=10,       # 设置连接池中保持的持久连接数
    max_overflow=20,    # 设置连接池允许创建的额外连接数
)

# 2. 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, # 绑定异步引擎
    expire_on_commit=False, # 关闭会话时，不自动提交事务
    class_=AsyncSession, # 使用异步会话类
)


# 3. 数据库会话依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session # 返回数据库会话，给路由处理函数
            await session.commit() # 提交事务
        except Exception:
            await session.rollback() # 回滚事务
            raise
        finally:
            await session.close() # 关闭会话