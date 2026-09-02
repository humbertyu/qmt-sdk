"""Install environment-dependent adapters from the official API snapshot."""

import inspect
import json
from importlib import resources


def load_official_api_spec():
    with resources.open_text("xtquant_compat", "official_xtdata_api.json", encoding="utf-8") as stream:
        return json.load(stream)


def _annotation(name):
    return {"str": str, "list": list, "int": int, "float": float, "bool": bool}.get(name, name)


def _signature(item):
    parameters = []
    for source in item["parameters"]:
        kind = getattr(inspect.Parameter, source["kind"])
        default = source.get("default", inspect.Parameter.empty)
        annotation = _annotation(source["annotation"]) if "annotation" in source else inspect.Parameter.empty
        parameters.append(inspect.Parameter(
            source["name"], kind=kind, default=default, annotation=annotation,
        ))
    return inspect.Signature(parameters)


def install_missing_api(module_globals, request):
    spec = load_official_api_spec()
    for item in spec["functions"]:
        name = item["name"]
        if callable(module_globals.get(name)):
            continue
        signature = _signature(item)

        def adapter(*args, __name=name, __signature=signature, **kwargs):
            bound = __signature.bind(*args, **kwargs)
            bound.apply_defaults()
            return request(__name, **bound.arguments)

        adapter.__name__ = name
        adapter.__qualname__ = name
        adapter.__doc__ = "Environment-dependent adapter for xtquant.xtdata.%s." % name
        adapter.__module__ = module_globals.get("__name__", "xtquant_compat.xtdata")
        adapter.__signature__ = signature
        module_globals[name] = adapter
    return spec
