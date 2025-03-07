import os

# 获取主程序的路径
main_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 将主程序路径设定为包的属性
__main_path__ = main_path
CONFIG_PATH = os.path.join(main_path, "config", "custom_key.toml")
print(f"config path: {CONFIG_PATH}")