"""
角色数据模型

定义角色实体和权限关联
"""

from tortoise.models import Model
from tortoise import fields


class Role(Model):
    """角色模型"""
    
    id = fields.IntField(pk=True, description="角色ID")
    name = fields.CharField(max_length=50, unique=True, description="角色名称")
    description = fields.CharField(max_length=200, null=True, description="角色描述")
    is_active = fields.BooleanField(default=True, description="是否激活")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    # 关联字段
    users = fields.ManyToManyField(
        "models.User", 
        related_name="roles", 
        through="user_roles",
        description="角色用户"
    )
    permissions = fields.ManyToManyField(
        "models.Permission", 
        related_name="roles", 
        through="role_permissions",
        description="角色权限"
    )
    
    class Meta:
        table = "roles"
        description = "角色表"
    
    async def get_permission_count(self) -> int:
        """获取角色权限数量"""
        return await self.permissions.all().count()
    
    async def get_user_count(self) -> int:
        """获取角色用户数量"""
        return await self.users.filter(is_active=True).count()
    
    def __str__(self):
        return f"Role(id={self.id}, name='{self.name}')"