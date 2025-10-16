import copy


def create_key_domain_name(order_of_keys: list[str]):
    return "/".join(order_of_keys)


def create_one_level_dict_from_multilayer_dict(dict_obj: dict):
    result = dict()

    def __inner_recursive_runner(base_path: str, dict_obj: dict):
        result = dict()
        for k, v in dict_obj.items():
            domain_key = create_key_domain_name([base_path, str(k)])
            if isinstance(v, dict):
                result.update(__inner_recursive_runner(domain_key, v))
            else:
                result[domain_key] = copy.deepcopy(v)
        return result

    for k, v in dict_obj.items():
        if isinstance(v, dict):
            result.update(__inner_recursive_runner(str(k), v))
        else:
            result[str(k)] = copy.deepcopy(v)
    return result
