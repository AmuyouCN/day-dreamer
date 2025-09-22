"""
用户数据模型

定义用户实体和相关操作
"""

from tortoise.models import Model
from tortoise import fields
from app.core.security import verify_password, get_password_hash


class User(Model):
    """用户模型"""
    
    id = fields.IntField(pk=True, description="用户ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    email = fields.CharField(max_length=100, unique=True, description="邮箱地址")
    password_hash = fields.CharField(max_length=255, description="密码哈希")
    full_name = fields.CharField(max_length=100, null=True, description="用户全名")
    is_active = fields.BooleanField(default=True, description="是否激活")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")
    
    # 关联字段
    roles = fields.ManyToManyField(
        "models.Role", 
        related_name="users", 
        through="user_roles",
        description="用户角色"
    )
    created_apis = fields.ReverseRelation["ApiDefinition"]
    created_test_cases = fields.ReverseRelation["TestCase"]
    personal_variables = fields.ReverseRelation["Variable"]
    test_executions = fields.ReverseRelation["TestExecution"]
    
    class Meta:
        table = "users"
        description = "用户表"
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return verify_password(password, self.password_hash)
    
    def set_password(self, password: str):
        """设置密码"""
        self.password_hash = get_password_hash(password)
    
    async def get_permissions(self) -> list:
        """获取用户权限列表"""
        permissions = []
        roles = await self.roles.all().prefetch_related("permissions")
        
        for role in roles:
            if role.is_active:
                role_permissions = await role.permissions.all()
                for perm in role_permissions:
                    permission_key = f"{perm.resource}:{perm.action}"
                    if permission_key not in permissions:
                        permissions.append(permission_key)
        
        return permissions
    
    def __str__(self):
        return f"User(id={self.id}, username='{self.username}')"