# 封装openai function call
import json
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, List, Callable
from loguru import logger


# 定义一个装饰器，用于将函数描述数据转换为可调用的方法函数
def function_factory(name, description, parameters):
    def decorator(func):
        def wrapper(params):
            # 根据参数字典调用实际函数
            return func(**params)

        # 添加一些元数据到生成的函数上
        wrapper.__name__ = name
        wrapper.__doc__ = description
        wrapper.__annotations__ = parameters
        return wrapper

    return decorator


class Parameter(BaseModel):
    type: str
    properties: Dict[str, Any]
    required: List[str]

class Function(BaseModel):
    name: str
    description: str
    parameters: Parameter = None

# 定义工具基类
class BaseTool:
    def _tool_info(self):
        print(self.parameters)
        info = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    key: {"type": "string", "description": f"{key} description"} for key in self.parameters.keys()
                } if self.parameters else None,
                "required": list(self.parameters.keys()) if self.parameters else None
            }
        }
        return info  # 返回字典而不是 JSON 字符串

# 函数注册
class FunctionRegistry:
    
    

    def __init__(self):
        self._registry = {}
        # self._registry_list = []
        self.func_names = []
        self._functions = []
        self._tools = {}
    
    def register_function(self, obj):
        self._tools[obj.name] = obj
        self._register_function(**obj._tool_info(), func=obj._run)

    def _register_function(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        decorated_func = function_factory(name, description, parameters)(func)
        self._registry[name] = decorated_func
        # self._registry_list.append(Function(name=name, description=description, parameters=parameters))
        # FunctionRegistry._functions.append({
        #     "name": name,
        #     "description": description,
        #     "parameters": parameters
        # })
        ## vllm 需要"function"  
        self._functions.append({"function":{
            "name": name,
            "description": description,
            "parameters": parameters
        }})
        print(f"Registering function ||: {name}")
        self.func_names.append(name)


    def get_function(self, name: str) -> Callable:
        return self._registry.get(name, None)
    
    def get_tool_from_name(self, name: str):
        return self._tools.get(name, None)

    def exec_func(self, name: str, params: Dict[str, Any]):
        func = self.get_function(name)
        if func is None:
            raise ValueError(f"Function {name} not found, Now available functions: {self.func_names}")
        # execute
        exec_res = func(params)
        logger.info(f">>: exec_func  name: {name}")
        return exec_res


class FunctionCallHandler:
    def __init__(self, function_call: Dict[str, Any], function_map: Dict[str, Any]):
        self.function_call = function_call
        self.function_name = function_call.name
        self.arguments = json.loads(function_call.arguments)
        self.function_map = function_map
        self.func_names = getattr(function_map,"func_names",None)

    def call_function(self):
        if self.function_name not in self.func_names:
            # print(f"Unsupported function: {self.function_name}")
            return "Unsupported function"

        function, input_model, output_model = self.function_map.get_function(self.function_name)
        
        try:
            # 校验输入格式
            validated_input = input_model(**self.arguments)
        except ValidationError as e:
            return f"Input validation error: {e}"
        
        # 调用函数
        result = function(**validated_input.dict())
        
        try:
            # 校验输出格式
            validated_output = output_model(result=result)
        except ValidationError as e:
            return f"Output validation error: {e}"
        
        return validated_output.dict()
    