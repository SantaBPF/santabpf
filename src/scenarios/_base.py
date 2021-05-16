from util import _validator


class ScenarioMeta(type):

    @staticmethod
    def has_method(obj, name):
        return callable(getattr(obj, name, None))

    def __call__(cls, *args, **kwargs):
        instance = type.__call__(cls, *args, **kwargs)

        has_check = cls.has_method(instance, 'check')
        has_trigger = cls.has_method(instance, 'trigger')

        if not (has_check ^ has_trigger):
            raise NotImplementedError('Scenario must have either check() or trigger() not both.')

        has_troubleshoot = cls.has_method(instance, 'troubleshoot')

        if not has_troubleshoot:
            raise NotImplementedError('Scenario must have troubleshoot().')

        return instance


class Scenario(metaclass=ScenarioMeta):
    """
    모든 시나리오들이 공통적으로 가져야할 메서드들을 명세한 클래스
    """

    default_param = {}

    def __init__(self, param=None):
        self.param = param

    def validate(self):
        if getattr(self, 'default_param'):
            _validator.set_default_param(self.param, self.default_param)

    # def monitor(self):
    # def trigger(self):

    # def troubleshoot(self):
