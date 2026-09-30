"""Prototype explicit Collection typing; formal placement remains Board-review work."""

def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values(): yield from nodes(child)
    elif isinstance(value, list):
        for child in value: yield from nodes(child)

def collection_types(assessment):
    registry=assessment.get('collections',{})
    types={}
    active=set()
    def bind(name,capability):
        if name not in registry: raise ValueError(f'Unknown Collection reference: {name}')
        if not isinstance(capability,str) or '.' not in capability:
            raise ValueError(f'Missing Collection capability: {name}')
        if name in active: raise ValueError(f'Collection dependency cycle: {name}')
        if name in types:
            if types[name]!=capability: raise ValueError(f'Conflicting Collection capability: {name}')
            return
        types[name]=capability
        active.add(name)
        for item in nodes(registry[name].get('set',{})):
            if isinstance(item.get('collection'),str): bind(item['collection'],capability)
        active.remove(name)
    for test in assessment.get('tests',{}).values():
        if isinstance(test.get('collection'),str): bind(test['collection'],test.get('capability'))
    for var in assessment.get('variables',{}).values():
        for name,capability in var.get('collection_capabilities',{}).items(): bind(name,capability)
        for item in nodes(var.get('expression',{})):
            values=item.get('values')
            if isinstance(values,dict) and isinstance(values.get('collection'),dict):
                if 'capability' in values['collection']:
                    raise ValueError('Embedded Collection capability belongs on its Variable')
                capability=var.get('capability')
                if not isinstance(capability,str) or '.' not in capability:
                    raise ValueError('Embedded Collection has no Variable capability')
                for member in nodes(values['collection'].get('set',{})):
                    if isinstance(member.get('collection'),str): bind(member['collection'],capability)
        for item in nodes(var.get('expression',{})):
            values=item.get('values')
            if isinstance(values,dict) and isinstance(values.get('collection'),str):
                if values['collection'] not in registry:
                    raise ValueError(f"Unknown Collection reference: {values['collection']}")
    for name in registry:
        if 'capability' in registry[name]: raise ValueError(f'Collection capability declaration belongs on Test or Variable: {name}')
        if name not in types: raise ValueError(f'Missing Collection capability binding: {name}')
    return types

def place_capabilities(assessment):
    """Move original source types to Tests or explicit Variable-side bindings."""
    registry=assessment['collections']
    original={name:payload['capability'] for name,payload in registry.items()}
    # Test contracts also type descendants reached through their Collection sets.
    bound={}
    def bind(name,cap):
        if original[name]!=cap: raise ValueError(f'Collection capability mismatch: {name}')
        if name in bound:
            if bound[name]!=cap: raise ValueError(f'Conflicting Collection capability: {name}')
            return
        bound[name]=cap
        for item in nodes(registry[name].get('set',{})):
            if isinstance(item.get('collection'),str): bind(item['collection'],cap)
    for test in assessment['tests'].values():
        if isinstance(test.get('collection'),str): bind(test['collection'],test['capability'])
        assertion=test.get('assertion',{})
        assertion.pop('state_capability',None)
        for state in assertion.get('states',[]): state.pop('capability',None)
    for var in assessment.get('variables',{}).values():
        bindings={}
        for item in nodes(var.get('expression',{})):
            values=item.get('values')
            if isinstance(values,dict) and isinstance(values.get('collection'),str):
                name=values['collection']
                if name not in bound: bindings[name]=original[name]
        if bindings: var['collection_capabilities']=bindings
    for name,payload in registry.items():
        cap=payload.pop('capability')
        for item in nodes(payload):
            if 'match' in item and 'capability' in item:
                if item['capability']!=cap: raise ValueError(f'Filter capability mismatch: {name}')
                del item['capability']
    resolved=collection_types(assessment)
    if resolved!=original: raise ValueError('Collection typing changed during declaration placement')
    return assessment
