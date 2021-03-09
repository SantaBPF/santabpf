class ScenarioMeta(type):
    def has_method(self, obj, name):
        return callable(getattr(obj, name, None))

    def __call__(self, *args, **kwargs):
        cls = type.__call__(self, *args)

        has_monitor = self.has_method(cls, 'monitor')
        has_trigger = self.has_method(cls, 'trigger')

        if not (has_monitor ^ has_trigger):
            raise Exception

        has_troubleshoot = self.has_method(cls, 'troubleshoot')

        if not has_troubleshoot:
            raise Exception

        return cls


class Scenario(metaclass=ScenarioMeta):
    """
    모든 시나리오들이 공통적으로 가져야할 메서드들을 명세한 클래스
    """

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

    # def monitor(self):
    # def trigger(self):

    # def troubleshoot(self):
