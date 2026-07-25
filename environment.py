class Environment:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent  # Can be an Environment instance or a dict

    def get(self, name, default=None):
        if name in self.bindings:
            return self.bindings[name]
        elif isinstance(self.parent, Environment):
            return self.parent.get(name, default)
        elif isinstance(self.parent, dict) and name in self.parent:
            return self.parent[name]
        elif default is not None:
            return default
        else:
            raise RuntimeError(f"Error : Variable '{name}' not declared")

    def set(self, name, value):
        if name in self.bindings:
            self.bindings[name] = value
        elif isinstance(self.parent, Environment) and self.parent.contains(name):
            self.parent.set(name, value)
        elif isinstance(self.parent, dict) and name in self.parent:
            self.parent[name] = value
        else:
            self.bindings[name] = value

    def contains(self, name):
        if name in self.bindings:
            return True
        if isinstance(self.parent, Environment):
            return self.parent.contains(name)
        if isinstance(self.parent, dict):
            return name in self.parent
        return False

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, name, value):
        self.set(name, value)

    def __contains__(self, name):
        return self.contains(name)