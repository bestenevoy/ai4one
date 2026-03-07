import time

class Agent:
    def __init__(self, name, role, tools=None):
        self.name = name
        self.role = role
        self.tools = tools if tools else []
        self.knowledge = {} # 模拟智能体的知识或状态

    def act(self, task, shared_state):
        """
        智能体根据任务和共享状态执行动作
        """
        print(f"--- {self.name} ({self.role}) 正在处理任务：{task['description']} ---")
        time.sleep(0.5) # 模拟处理时间

        if self.role == "ThinkingAgent":
            print(f"{self.name}: 分析任务，规划下一步行动。")
            # 思考智能体决定激活哪个其他智能体
            if "research" in task["description"].lower():
                next_agent = "SearchAgent"
            elif "calculation" in task["description"].lower():
                next_agent = "CodeAgent"
            else:
                next_agent = "ReflectionAgent" # 默认反射

            shared_state["next_agent"] = next_agent
            shared_state["thinking_output"] = f"思考：决定激活 {next_agent} 处理任务。"

        elif self.role == "SearchAgent":
            keyword = task["description"].split(":")[-1].strip()
            print(f"{self.name}: 使用工具 {self.tools} 搜索关键词 '{keyword}'...")
            search_result = f"关于 '{keyword}' 的搜索结果：找到相关信息。"
            shared_state["search_output"] = search_result
            shared_state["next_agent"] = "ThinkingAgent" # 搜索完成后返回思考智能体
            print(f"{self.name}: {search_result}")

        elif self.role == "CodeAgent":
            equation = task["description"].split(":")[-1].strip()
            print(f"{self.name}: 使用工具 {self.tools} 执行代码计算 '{equation}'...")
            try:
                result = eval(equation) # 简单模拟代码执行
                calculation_output = f"计算 '{equation}' 结果为: {result}"
            except Exception as e:
                calculation_output = f"计算出错: {e}"
            shared_state["calculation_output"] = calculation_output
            shared_state["next_agent"] = "ThinkingAgent" # 计算完成后返回思考智能体
            print(f"{self.name}: {calculation_output}")

        elif self.role == "ReflectionAgent":
            print(f"{self.name}: 反思当前状态和已完成的工作...")
            reflection_output = f"反思：已完成 {len(shared_state)} 步，任务进展顺利。"
            shared_state["reflection_output"] = reflection_output
            shared_state["task_completed"] = True # 模拟任务完成
            print(f"{self.name}: {reflection_output}")

        print("-" * 50)
        return shared_state

class ChainOfAgentsSystem:
    def __init__(self):
        self.agents = {
            "ThinkingAgent": Agent("思考智能体", "ThinkingAgent"),
            "SearchAgent": Agent("搜索智能体", "SearchAgent", tools=["WebSearch", "CrawlPage"]),
            "CodeAgent": Agent("代码智能体", "CodeAgent", tools=["PythonInterpreter"]),
            "ReflectionAgent": Agent("反思智能体", "ReflectionAgent")
        }
        self.shared_state = {}

    def run_task(self, initial_task):
        self.shared_state = {"initial_task": initial_task["description"]}
        current_agent_name = "ThinkingAgent"
        max_steps = 10
        step = 0

        while step < max_steps and not self.shared_state.get("task_completed"):
            agent = self.agents[current_agent_name]
            self.shared_state = agent.act(initial_task, self.shared_state)
            current_agent_name = self.shared_state.get("next_agent", "ThinkingAgent")
            step += 1
            if self.shared_state.get("task_completed"):
                print("任务完成！")
                break
            elif step == max_steps:
                print("达到最大步数，任务可能未完全解决。")

        print("\n--- 最终共享状态 ---")
        for key, value in self.shared_state.items():
            print(f"{key}: {value}")

# 示例使用
if __name__ == "__main__":
    coa_system = ChainOfAgentsSystem()

    print("--- 任务1: 研究: 大型语言模型最新进展 ---")
    task1 = {"description": "研究: 大型语言模型最新进展"}
    coa_system.run_task(task1)

    print("\n--- 任务2: 计算: 2 + 3 * 4 ---")
    task2 = {"description": "计算: 2 + 3 * 4"}
    coa_system.run_task(task2)

    print("\n--- 任务3: 简单任务 ---")
    task3 = {"description": "简单任务"}
    coa_system.run_task(task3)