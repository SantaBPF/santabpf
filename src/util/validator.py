def set_default_param(param, default_param):
    for key, item in default_param.items():
        param[key] = param.get(key, item)