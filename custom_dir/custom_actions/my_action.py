import json
from time import sleep
from datetime import datetime
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from custom_dir.account import find_role_info, get_all_rolenames
from custom_dir.my_logger import custom_logger as logger

@AgentServer.custom_action("OverrideLoginInfo")
class MyAction1(CustomAction):

    def run(self, context: Context, argv: CustomAction.RunArg) -> CustomAction.RunResult:
        cus_param = json.loads(argv.custom_action_param)
        # print(cus_param)
        account = cus_param['account']
        platform = cus_param['platform']
        servername = cus_param['servername']
        context.override_pipeline({"TASK-A-4找到匹配的账号了并点击":{"expected": account}})
        context.override_pipeline({"TASK-A-6检测平台按钮并点击":{"template": "平台区服/"+platform+".png"}})
        context.override_pipeline({"TASK-A-9查找区服图标并点击选择该角色":{"template": "平台区服/"+servername+".png"}})
        #print(f"##CustomAction## OverrideLoginInfoAction 覆写登录账号为：{account}, 平台：{platform}, 区服：{servername}")
        
        return CustomAction.RunResult(success=True)

@AgentServer.custom_action("RunTaskList")
class RunTaskListAction(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> CustomAction.RunResult:
        logger.debug(f"argv.custom_action_param: {argv.custom_action_param}")
        cus_param = json.loads(argv.custom_action_param)
        
        tasks = cus_param['tasks']
        logger.info(f"传入的 tasks 参数为：{tasks}")

        for task in tasks:
            task_detail = context.run_task(task["taskname"])
            sleep(task["wait"])

@AgentServer.custom_action("ForRolesToRunTask")
class MyAction2(CustomAction):
    
    def run(self, context: Context, argv: CustomAction.RunArg) -> CustomAction.RunResult:
        logger.debug(f"argv.custom_action_param: {argv.custom_action_param}")
        cus_param = json.loads(argv.custom_action_param)
        logger.debug(f"cus_param： {cus_param}")
        
        tasks = cus_param['tasks']
        logger.info(f"传入的 tasks 参数为：{tasks}")

        rolenames_str = cus_param['rolenames']
        logger.info(f"传入的 rolenames_str 参数：{rolenames_str}, 类型为：{type(rolenames_str)}")

        if type(rolenames_str) == str:
            try:
                rolenames = eval(rolenames_str)
                logger.debug(f"eval 成功，结果：{rolenames}")
            except Exception as e:
                logger.debug(f"rolenames_str 参数转换为列表失败: {str(e)}，尝试解析逗号分隔的格式", exc_info=True)
                rolenames = rolenames_str.split(',')
        elif type(rolenames_str) == list:
            rolenames = rolenames_str
        else:
            rolenames = []
        
        all_num = len(rolenames)
        logger.info(f"解析后的角色数量：{all_num}, 角色名：{rolenames}")


        if rolenames and rolenames[0] == "ALL":
            rolenames = get_all_rolenames()
        
        for index, rolename in enumerate(rolenames):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"{now} 当前任务角色 {rolename}, {index}/{all_num}")
            info = find_role_info(rolename)
            if not info:
                continue

            context.override_pipeline(
                {
                    "重写账号角色信息": {
                        "custom_action_param": {
                            "account": info['account'],
                            "platform": info['platform'],
                            "servername": info['servername']
                        }
                    }
                }
            )
            # context.override_pipeline({"TASK-A-6检测平台按钮并点击":{"template": "平台区服/"+info['platform']+".png"}})
            # context.override_pipeline({"TASK-A-9查找区服图标并点击选择该角色":{"template": "平台区服/"+info['servername']+".png"}})

            for task in tasks:
                task_detail = context.run_task(task["taskname"])
                # print("##Task Detail##", task_detail)
                sleep(task["wait"])
            
        context.run_task("TASK-关闭游戏")

