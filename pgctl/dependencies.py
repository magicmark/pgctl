from .errors import CircularDependencies


def topological_sort(services, dependency_map):
    """Sort services so that dependencies come before dependents.

    :param services: iterable of service objects (must have .name attribute)
    :param dependency_map: dict mapping service name -> list of service names it depends on
    :return: list of services in dependency order
    """
    service_by_name = {s.name: s for s in services}
    service_names = set(service_by_name.keys())

    adj = {name: [] for name in service_names}
    for name in service_names:
        for dep in dependency_map.get(name, ()):
            if dep in service_names:
                adj[dep].append(name)

    UNVISITED, IN_PROGRESS, DONE = 0, 1, 2
    state = {name: UNVISITED for name in service_names}
    order = []

    def visit(name):
        if state[name] == DONE:
            return
        if state[name] == IN_PROGRESS:
            raise CircularDependencies(
                "Circular dependency detected involving service '%s'" % name
            )
        state[name] = IN_PROGRESS
        for neighbor in adj[name]:
            visit(neighbor)
        state[name] = DONE
        order.append(name)

    for name in sorted(service_names):
        visit(name)

    order.reverse()
    return [service_by_name[name] for name in order if name in service_by_name]


def resolve_start_order(services, dependency_map):
    """Return services ordered so dependencies start first.

    Also includes any transitive dependencies from dependency_map that are
    not already in the requested services list.
    """
    service_by_name = {s.name: s for s in services}
    needed = set(service_by_name.keys())

    queue = list(needed)
    while queue:
        name = queue.pop()
        for dep in dependency_map.get(name, ()):
            if dep not in needed:
                needed.add(dep)
                queue.append(dep)

    return topological_sort(
        [service_by_name[n] for n in needed if n in service_by_name],
        dependency_map,
    )


def resolve_stop_order(services, dependency_map):
    """Return services ordered so dependents stop first (reverse of start)."""
    return list(reversed(resolve_start_order(services, dependency_map)))
