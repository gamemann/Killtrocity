import json

class Config():
    def __init__(self):
        # Initialize CFG file and config dict.
        self.cfg_file = "/etc/killtrocity/killtrocity.json"
        self.cfg = {}

        # Set defaults.
        self.set_defaults()

        # Import
        self.import_file(self.cfg_file)

    def import_file(self, file_name: str):
        # Attempt to open file in read mode.
        try:
            file = open(file_name, "r")
        except Exception as e:
            print("Failed to open file '" + file_name + "' for import!")
            print(e)
            
            return

        # Now try to parse JSON and update existing CFG dict.
        try:
            self.cfg.update(json.load(file))
        except json.JSONDecodeError as e:
            print("Could not parse JSON during import.")
            print(e)

    # Set default functions.
    def set_defaults(self):
        self.set("kf_addr", "127.0.0.1")
        self.set("kf_port", 8003)
        self.set("km_socket_path", "/etc/kilimanjaro/server.sock")
        self.set("alive_timeout", 10)
        self.set("alive_max_fails", 5)
        self.set("alive_interval", 5)
        self.set("ssl", False)
        self.set("stress", False)
        self.set("stress_array_size", 4096)
        self.set("stress_count", 50)

    # Retrieves CFG value.
    def get(self, key: str):
        return self.cfg[key]

    # Sets a CFG value.
    def set(self, key: str, val):
        self.cfg[key] = val

cfg = Config()