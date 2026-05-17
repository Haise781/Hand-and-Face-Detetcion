import os
import importlib
import inspect
from plugins.base_plugin import BasePlugin

class PluginManager:
    def __init__(self):
        self.plugins = []
        self.load_plugins()

    def load_plugins(self):
        """Dynamically loads all plugins in the plugins directory inheriting from BasePlugin"""
        self.plugins = []
        plugins_dir = os.path.dirname(__file__)
        
        # Ensure directory is scanned correctly
        if not os.path.exists(plugins_dir):
            print(f"[ERROR] Plugins directory '{plugins_dir}' does not exist.")
            return

        for file in os.listdir(plugins_dir):
            if file.endswith(".py") and file not in ["__init__.py", "base_plugin.py", "manager.py"]:
                module_name = f"plugins.{file[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    # Reload module to fetch any updates
                    importlib.reload(module)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj != BasePlugin:
                            # Instantiate the plugin
                            plugin_instance = obj()
                            self.plugins.append(plugin_instance)
                            print(f"[PLUGIN SYSTEM] Loaded plugin: {plugin_instance.name} ({name})")
                except Exception as e:
                    print(f"[PLUGIN SYSTEM] Failed to load plugin from {file}: {e}")

    def get_plugins(self):
        """Returns a list of all loaded plugins"""
        return self.plugins

    def process_gesture(self, hand_index: int, gesture: str, lm_list: list, frame, results) -> list:
        """
        Processes a detected gesture against enabled plugins and executes matches.
        Returns:
            A list of status messages returned by executed plugins.
        """
        logs = []
        for plugin in self.plugins:
            if plugin.enabled:
                # Direct trigger match, or special case (Volume Control handles both Thumbs Up/Down)
                is_match = False
                if isinstance(plugin.gesture_trigger, list):
                    is_match = gesture in plugin.gesture_trigger
                else:
                    is_match = (gesture == plugin.gesture_trigger)
                
                # Special wildcard or advanced mapping check
                if not is_match and plugin.name == "Volume Control" and gesture in ["Thumbs Up", "Thumbs Down"]:
                    is_match = True

                if is_match:
                    try:
                        log_msg = plugin.execute(hand_index, lm_list, frame, results)
                        if log_msg:
                            logs.append(f"[{plugin.name}] {log_msg}")
                    except Exception as e:
                        logs.append(f"[{plugin.name}] Error: {str(e)}")
        return logs
