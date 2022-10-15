from typing import List
from pathlib import Path
import json
import time
import os
from deta import Drive
from currency_converter import CurrencyConverter, SINGLE_DAY_ECB_URL


cc = CurrencyConverter(SINGLE_DAY_ECB_URL)


DETA_DRIVER_NAME = "dividend-calculator"

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

			# Check if this is running on Deta
			project_key = os.getenv("DETA_PROJECT_KEY")
			deta_file = f"{file_prefix}_{file_sufix}.json"
			if project_key is not None:
				drive = Drive(DETA_DRIVER_NAME)
				file = drive.get(deta_file)
				if file is not None:
					return json.loads(file.read())

			if cache_file_path.is_file():
				
				now = int(time.time())
				created_at = int(cache_file_path.stat().st_mtime)

				if now < created_at + ttl_sec:
					# print("Get data from cache")
					with open(cache_file_path, "r") as file:
						return json.loads(file.read())

			# print("Get data from source")
			result = func(*args, **kwargs)

			# Check if this is running on Deta
			if project_key is not None:
				drive = Drive(DETA_DRIVER_NAME)
				drive.put(deta_file, data=json.dumps(result))

				return result

			with open(cache_file_path, "w") as file:
				file.write(json.dumps(result, indent=4, ensure_ascii=False))

			return result
		return wrapper
	return cache


def clear_deta_cache():
	drive = Drive(DETA_DRIVER_NAME)

	files = drive.list()
	if files is None:
		return

	drive.delete_many(files["names"])
	print("deleted all files in cache")


def growth_in_percentage(data: List[float])-> List[float]:
	initial = data[0]
	res = [0]
	for d in data[1:]:
		res.append(calc_percentage_diff(initial, d))

	return res

def to_GBP(amount: float, from_currency: str)-> float:
	if from_currency == "GBp":
		return amount / 100

	return cc.convert(amount, from_currency, "GBP")

