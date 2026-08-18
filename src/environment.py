_SENTINEL = object()

class Environment:
    def __init__(self, parent=None):
        self.bindings = {}
        self.immutable = set()
        self.parent = parent  # Can be an Environment instance or a dict
        self.hooks = {}

    def add_hook(self, name, hook_fn):
        if name not in self.hooks:
            self.hooks[name] = []
        self.hooks[name].append(hook_fn)

    def trigger_hooks(self, name, new_value):
        if name in self.hooks:
            for hook in self.hooks[name]:
                hook(new_value)
        if isinstance(self.parent, Environment):
            self.parent.trigger_hooks(name, new_value)

    def is_immutable(self, name):
        """Check if variable is declared as fix(immuable)"""
        if name in self.immutable:
            return True
        if isinstance(self.parent, Environment):
            return self.parent.is_immutable(name)
        return False
    def mark_immutable(self, name):
        if name in self.bindings:
            self.immutable.add(name)
        elif isinstance(self.parent, Environment):
            self.parent.mark_immutable(name)

    def get(self, name, default=None):
        if name in self.bindings:
            return self.bindings[name]
        elif isinstance(self.parent, Environment):
            return self.parent.get(name, default)
        elif isinstance(self.parent, dict) and name in self.parent:
            return self.parent[name]
        elif default is not _SENTINEL:
            return default
        else:
            raise RuntimeError(f"Error : Variable '{name}' not declared")
    
    def set(self, name, value):
        if name in self.bindings:
            self.trigger_hooks(name, value)
            self.bindings[name] = value
        elif isinstance(self.parent, Environment) and self.parent.contains(name):
            self.parent.set(name, value)
        elif isinstance(self.parent, dict) and name in self.parent:
            self.parent[name] = value
        else:
            self.trigger_hooks(name, value)
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