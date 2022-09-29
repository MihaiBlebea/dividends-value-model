from pathlib import Path
import json
import time


def safeget(dct: dict, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def calc_percentage_diff(initial: float, current: float)-> float:
    return abs(initial - current) / current

def cache_factory(cache_dir: str, file_prefix: str, ttl_sec: int):
    def cache(func):
        def wrapper(*args, **kwargs):

            args_params = [str(argv) for argv in args[1:]]
            kwargs_params = [str(argv) for argv in list(kwargs.values())]

            file_sufix = "_".join(args_params + kwargs_params)

            Path(cache_dir).mkdir(parents=True, exist_ok=True)

            cache_file_path = Path(f"{cache_dir}/{file_prefix}_{file_sufix}.json")
            if cache_file_path.is_file():
                
                now = int(time.time())
                created_at = int(cache_file_path.stat().st_mtime)

                if now < created_at + ttl_sec:
                    # print("Get data from cache")
                    with open(cache_file_path, "r") as file:
                        return json.loads(file.read())

            # print("Get data from source")
            result = func(*args, **kwargs)

            with open(cache_file_path, "w") as file:
                file.write(json.dumps(result, indent=4, ensure_ascii=False))

            return result
        return wrapper
    return cache