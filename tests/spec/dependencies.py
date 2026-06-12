import pytest

from pgctl.dependencies import resolve_start_order
from pgctl.dependencies import resolve_stop_order
from pgctl.dependencies import topological_sort
from pgctl.errors import CircularDependencies


class FakeService:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'FakeService({self.name!r})'

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class DescribeTopologicalSort:

    def it_handles_no_dependencies(self):
        services = [FakeService('a'), FakeService('b'), FakeService('c')]
        result = topological_sort(services, {})
        assert set(s.name for s in result) == {'a', 'b', 'c'}

    def it_sorts_a_linear_chain(self):
        services = [FakeService('db'), FakeService('api'), FakeService('web')]
        deps = {'api': ['db'], 'web': ['api']}
        result = topological_sort(services, deps)
        names = [s.name for s in result]
        assert names.index('db') < names.index('api')
        assert names.index('api') < names.index('web')

    def it_sorts_a_diamond_dependency(self):
        services = [FakeService('db'), FakeService('cache'), FakeService('api'), FakeService('web')]
        deps = {'api': ['db', 'cache'], 'web': ['api']}
        result = topological_sort(services, deps)
        names = [s.name for s in result]
        assert names.index('db') < names.index('api')
        assert names.index('cache') < names.index('api')
        assert names.index('api') < names.index('web')

    def it_raises_on_circular_dependency(self):
        services = [FakeService('a'), FakeService('b')]
        deps = {'a': ['b'], 'b': ['a']}
        with pytest.raises(CircularDependencies):
            topological_sort(services, deps)

    def it_ignores_dependencies_not_in_service_list(self):
        services = [FakeService('api')]
        deps = {'api': ['db']}
        result = topological_sort(services, deps)
        assert [s.name for s in result] == ['api']


class DescribeResolveStartOrder:

    def it_orders_dependencies_before_dependents(self):
        services = [FakeService('web'), FakeService('api'), FakeService('db')]
        deps = {'api': ['db'], 'web': ['api']}
        result = resolve_start_order(services, deps)
        names = [s.name for s in result]
        assert names.index('db') < names.index('api')
        assert names.index('api') < names.index('web')


class DescribeResolveStopOrder:

    def it_orders_dependents_before_dependencies(self):
        services = [FakeService('web'), FakeService('api'), FakeService('db')]
        deps = {'api': ['db'], 'web': ['api']}
        result = resolve_stop_order(services, deps)
        names = [s.name for s in result]
        assert names.index('web') < names.index('api')
        assert names.index('api') < names.index('db')
