import os
import toml
from functools import wraps

def singleton(cls):
    instances = {}
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

class Configer:
    def __init__(self, config_path: str = "config/custom_key.toml"):
        self.__value = {}
        self.config_path = config_path

    def load(self):
        if self.config_path:
            try:
                with open(self.config_path, 'r') as file:
                    self.__value = toml.load(file)
            except FileNotFoundError:
                print(f"错误: 文件 '{self.config_path}' 不存在。")
            except toml.TomlDecodeError:
                print(f"错误: '{self.config_path}' 不是有效的TOML文件。")
            except Exception as e:
                print(f"发生错误: {str(e)}")

    def get(self, key, default=None):
        return self.__value.get(key, default)

    def set(self, key, value):
        self.__value[key] = value

    def save(self):
        if self.config_path:
            with open(self.config_path, 'w') as file:
                toml.dump(self.__value, file)

@singleton
class CustomKeyConfiger(Configer):
    """用于管理用户密钥。"""
    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        if config_path:
            self.load()
        if self.get("KEY_LIST"):
            for key, value in self.get("KEY_LIST").items():
                os.environ[key] = str(value)

    @property
    def keys(self):
        return self.get("KEY_LIST", {}).keys()

    def load(self):
        super().load()
        # 加载后立即更新环境变量
        if self.get("KEY_LIST"):
            for key, value in self.get("KEY_LIST").items():
                os.environ[key] = str(value)

    def set_key(self, key, value):
        key_list = self.get("KEY_LIST", {})
        key_list[key] = value
        self.set("KEY_LIST", key_list)
        os.environ[key] = str(value)

    def get_key(self, key, default=None):
        return self.get("KEY_LIST", {}).get(key, default)

    def remove_key(self, key):
        key_list = self.get("KEY_LIST", {})
        if key in key_list:
            del key_list[key]
            self.set("KEY_LIST", key_list)
        if key in os.environ:
            del os.environ[key]

# 使用示例
if __name__ == "__main__":
    config = CustomKeyConfiger("config/custom_key.toml")
    
    # 设置一个新的密钥
    # config.set_key("NEW_API_KEY", "sk-newkey123456")
    
    # 获取一个密钥
    print(config.get_key("DEEPSEEK_API_KEY"))
    print("==")
    print(config.keys)
    # 移除一个密钥
    # config.remove_key("DEEPSEEK_API_KEY")
    
    # 保存更改
    # config.save()

    print("环境变量:")
    for key in ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "NEW_API_KEY"]:
        print(f"{key}: {os.environ.get(key, 'Not set')}")