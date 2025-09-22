"""
权限数据模型

定义权限实体和操作
"""

from tortoise.models import Model
from tortoise import fields


class Permission(Model):
    """权限模型"""
    
    id = fields.IntField(pk=True, description="权限ID")
    name = fields.CharField(max_length=100, unique=True, description="权限名称")
    resource = fields.CharField(max_length=50, description="资源类型")
    action = fields.CharField(max_length=50, description="操作类型")
    description = fields.CharField(max_length=200, null=True, description="权限描述")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    
    # 关联字段
    roles = fields.ManyToManyField(
        "models.Role", 
        related_name="permissions", 
        through="role_permissions",
        description="权限角色"
    )
    
    class Meta:
        table = "permissions"
        description = "权限表"
        indexes = [
            ("resource", "action"),  # 资源和操作的组合索引
        ]
    
    @property
    def permission_key(self) -> str:
        """权限键"""
        return f"{self.resource}:{self.action}"
    
    def __str__(self):
        return f"Permission(id={self.id}, name='{self.name}')"