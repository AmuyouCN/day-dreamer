"""
用户业务服务

处理用户相关的业务逻辑
"""

from typing import Optional, List, Dict, Any
from tortoise.exceptions import IntegrityError
from tortoise.query_utils import Q

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.utils.exceptions import NotFoundError, ConflictError
from loguru import logger


class UserService:
    """用户服务类"""
    
    async def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        
        try:
            # 检查用户名是否已存在
            existing_user = await User.get_or_none(username=user_data.username)
            if existing_user:
                raise ConflictError(f\"用户名 '{user_data.username}' 已存在\")
            
            # 检查邮箱是否已存在
            existing_email = await User.get_or_none(email=user_data.email)
            if existing_email:
                raise ConflictError(f\"邮箱 '{user_data.email}' 已存在\")
            
            # 创建新用户
            user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                is_active=user_data.is_active
            )
            
            # 设置密码
            user.set_password(user_data.password)
            
            # 保存用户
            await user.save()
            
            logger.info(f\"用户创建成功: {user.username} (ID: {user.id})\")
            return user
            
        except IntegrityError as e:
            logger.error(f\"用户创建失败，数据库约束错误: {e}\")
            raise ConflictError(\"用户名或邮箱已存在\")
        except ConflictError:
            raise
        except Exception as e:
            logger.error(f\"用户创建失败: {e}\")
            raise
    
    async def get_user_by_id(self, user_id: int) -> User:
        \"\"\"根据ID获取用户\"\"\"
        
        user = await User.get_or_none(id=user_id)
        if not user:
            raise NotFoundError(f\"用户不存在: ID={user_id}\")
        
        return user
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        \"\"\"根据用户名获取用户\"\"\"
        return await User.get_or_none(username=username)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        \"\"\"更新用户信息\"\"\"
        
        user = await self.get_user_by_id(user_id)
        
        try:
            # 更新用户信息
            update_fields = []
            
            if user_data.username is not None:
                # 检查新用户名是否已存在
                if user_data.username != user.username:
                    existing_user = await User.get_or_none(username=user_data.username)
                    if existing_user:
                        raise ConflictError(f\"用户名 '{user_data.username}' 已存在\")
                user.username = user_data.username
                update_fields.append(\"username\")
            
            if user_data.email is not None:
                # 检查新邮箱是否已存在
                if user_data.email != user.email:
                    existing_email = await User.get_or_none(email=user_data.email)
                    if existing_email:
                        raise ConflictError(f\"邮箱 '{user_data.email}' 已存在\")
                user.email = user_data.email
                update_fields.append(\"email\")
            
            if user_data.full_name is not None:
                user.full_name = user_data.full_name
                update_fields.append(\"full_name\")
            
            if user_data.is_active is not None:
                user.is_active = user_data.is_active
                update_fields.append(\"is_active\")
            
            if update_fields:
                await user.save(update_fields=update_fields)
                logger.info(f\"用户信息更新成功: {user.username} (ID: {user.id})\")
            
            return user
            
        except ConflictError:
            raise
        except Exception as e:
            logger.error(f\"用户更新失败: {e}\")
            raise
    
    async def delete_user(self, user_id: int) -> bool:
        \"\"\"删除用户（软删除）\"\"\"
        
        user = await self.get_user_by_id(user_id)
        
        # 软删除：设置为非激活状态
        user.is_active = False
        await user.save(update_fields=[\"is_active\"])
        
        logger.info(f\"用户删除成功: {user.username} (ID: {user.id})\")
        return True
    
    async def list_users(
        self,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        \"\"\"获取用户列表\"\"\"
        
        # 构建查询条件
        query = User.all()
        
        if search:
            search_q = Q(username__icontains=search) | Q(email__icontains=search)
            if search:
                search_q |= Q(full_name__icontains=search)
            query = query.filter(search_q)
        
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        # 计算总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * size
        users = await query.offset(offset).limit(size).order_by(\"-created_at\")
        
        # 构建返回数据
        user_list = []
        for user in users:
            user_dict = {
                \"id\": user.id,
                \"username\": user.username,
                \"email\": user.email,
                \"full_name\": user.full_name,
                \"is_active\": user.is_active,
                \"created_at\": user.created_at.isoformat(),
                \"updated_at\": user.updated_at.isoformat(),
                \"last_login\": user.last_login.isoformat() if user.last_login else None
            }
            user_list.append(user_dict)
        
        return {
            \"users\": user_list,
            \"total\": total,
            \"page\": page,
            \"size\": size
        }
    
    async def get_user_roles(self, user_id: int) -> List[Role]:
        \"\"\"获取用户角色列表\"\"\"
        
        user = await self.get_user_by_id(user_id)
        roles = await user.roles.all()
        
        return roles
    
    async def assign_roles(self, user_id: int, role_ids: List[int]) -> bool:
        \"\"\"为用户分配角色\"\"\"
        
        user = await self.get_user_by_id(user_id)
        
        # 获取有效的角色
        roles = await Role.filter(id__in=role_ids, is_active=True)
        
        if len(roles) != len(role_ids):
            invalid_ids = set(role_ids) - {role.id for role in roles}
            raise NotFoundError(f\"角色不存在或已禁用: {invalid_ids}\")
        
        # 清除现有角色并分配新角色
        await user.roles.clear()
        await user.roles.add(*roles)
        
        logger.info(f\"用户角色分配成功: {user.username} -> {[role.name for role in roles]}\")
        return True
    
    async def remove_role(self, user_id: int, role_id: int) -> bool:
        \"\"\"移除用户角色\"\"\"
        
        user = await self.get_user_by_id(user_id)
        role = await Role.get_or_none(id=role_id)
        
        if not role:
            raise NotFoundError(f\"角色不存在: ID={role_id}\")
        
        await user.roles.remove(role)
        
        logger.info(f\"用户角色移除成功: {user.username} -> {role.name}\")
        return True
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        \"\"\"修改用户密码\"\"\"
        
        user = await self.get_user_by_id(user_id)
        
        # 验证旧密码
        if not user.verify_password(old_password):
            raise ConflictError(\"当前密码错误\")
        
        # 设置新密码
        user.set_password(new_password)
        await user.save(update_fields=[\"password_hash\"])
        
        logger.info(f\"用户密码修改成功: {user.username} (ID: {user.id})\")
        return True"