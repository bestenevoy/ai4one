#!/usr/bin/env python3
"""
MCP服务器验证脚本
验证本地的文件服务和待办服务是否正常工作

使用方法:
    python examples/mcp_validate.py
"""
import asyncio
import os
import sys
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "ai4one" / "mcp"

# 服务器脚本路径
FILE_SERVER_PATH = str(SRC_DIR / "local_file.py")
TODO_SERVER_PATH = str(SRC_DIR / "todo.py")

class MCPValidator:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_stack.aclose()
        
    async def connect_to_server(self, server_path: str, server_name: str):
        """连接到MCP服务器"""
        print(f"\n🔌 连接到 {server_name} 服务器...")
        print(f"   脚本路径: {server_path}")
        
        if not os.path.exists(server_path):
            raise FileNotFoundError(f"服务器脚本不存在: {server_path}")
            
        # 配置stdio参数
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None
        )
        
        # 建立连接
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport
        
        # 创建会话
        session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        
        # 初始化会话
        await session.initialize()
        print(f"✅ {server_name} 服务器连接成功")
        
        return session
        
    async def validate_file_server(self):
        """验证文件服务器"""
        print("\n📁 验证文件服务器功能...")
        
        try:
            session = await self.connect_to_server(FILE_SERVER_PATH, "文件服务")
            
            # 列出工具
            tools_response = await session.list_tools()
            tools = [tool.name for tool in tools_response.tools]
            print(f"   可用工具: {tools}")
            
            expected_tools = {
                "list_work_dir", "mkdir", "get_system_info", 
                "read_file", "open_dir", "write_file", 
                "delete_file", "run_command"
            }
            
            missing_tools = expected_tools - set(tools)
            if missing_tools:
                print(f"❌ 缺少工具: {missing_tools}")
                return False
                
            # 测试基本功能
            print("   测试 get_system_info...")
            result = await session.call_tool("get_system_info", {})
            print(f"   系统信息: {result.content[0].text}")
            
            print("   测试 list_work_dir...")
            result = await session.call_tool("list_work_dir", {})
            print(f"   工作目录内容: {result.content[0].text}")
            
            print("✅ 文件服务器验证通过")
            return True
            
        except Exception as e:
            print(f"❌ 文件服务器验证失败: {e}")
            return False
            
    async def validate_todo_server(self):
        """验证待办服务器"""
        print("\n📝 验证待办服务器功能...")
        
        try:
            session = await self.connect_to_server(TODO_SERVER_PATH, "待办服务")
            
            # 列出工具
            tools_response = await session.list_tools()
            tools = [tool.name for tool in tools_response.tools]
            print(f"   可用工具: {tools}")
            
            expected_tools = {
                "create_todo_list", "list_todo_lists", "get_todo_list",
                "delete_todo_list", "rename_todo_list", "add_task",
                "list_tasks", "set_task_status", "update_task",
                "remove_task", "clear_completed", "search_tasks"
            }
            
            missing_tools = expected_tools - set(tools)
            if missing_tools:
                print(f"❌ 缺少工具: {missing_tools}")
                return False
                
            # 测试基本功能
            print("   测试创建待办清单...")
            result = await session.call_tool("create_todo_list", {
                "name": "验证测试清单",
                "description": "用于验证MCP服务器的测试清单"
            })
            list_data = eval(result.content[0].text)  # 简单解析返回的dict
            list_id = list_data["id"]
            print(f"   创建的清单ID: {list_id}")
            
            print("   测试添加任务...")
            result = await session.call_tool("add_task", {
                "list_id": list_id,
                "content": "测试任务1",
                "priority": "high"
            })
            task_data = eval(result.content[0].text)
            task_id = task_data["id"]
            print(f"   创建的任务ID: {task_id}")
            
            print("   测试列出任务...")
            result = await session.call_tool("list_tasks", {"list_id": list_id})
            tasks = eval(result.content[0].text)
            print(f"   任务数量: {len(tasks)}")
            
            print("   测试更新任务状态...")
            result = await session.call_tool("set_task_status", {
                "list_id": list_id,
                "task_id": task_id,
                "status": "completed"
            })
            print("   任务状态已更新为completed")
            
            print("   清理测试数据...")
            await session.call_tool("delete_todo_list", {"list_id": list_id})
            print("   测试清单已删除")
            
            print("✅ 待办服务器验证通过")
            return True
            
        except Exception as e:
            print(f"❌ 待办服务器验证失败: {e}")
            return False
            
    async def run_validation(self):
        """运行完整验证"""
        print("🚀 开始MCP服务器验证...")
        print(f"项目根目录: {PROJECT_ROOT}")
        
        # 验证文件服务器
        file_server_ok = await self.validate_file_server()
        
        # 验证待办服务器  
        todo_server_ok = await self.validate_todo_server()
        
        # 总结
        print("\n📊 验证结果:")
        print(f"   文件服务器: {'✅ 通过' if file_server_ok else '❌ 失败'}")
        print(f"   待办服务器: {'✅ 通过' if todo_server_ok else '❌ 失败'}")
        
        if file_server_ok and todo_server_ok:
            print("\n🎉 所有MCP服务器验证通过!")
            return True
        else:
            print("\n⚠️  部分服务器验证失败，请检查错误信息")
            return False

async def main():
    """主函数"""
    try:
        async with MCPValidator() as validator:
            success = await validator.run_validation()
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 验证过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # 确保在正确的目录运行
    if not (PROJECT_ROOT / "pyproject.toml").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
        
    asyncio.run(main())