#!/usr/bin/env python3
import ast
import json
import re

# Read and transform a .po file to something easier to work with
def _parse_po(path):
	parameter_regex = re.compile(r"^#\. Parameter ([0-9]+): ([^ \r\n]+).*$")
	plural_regex = re.compile(r"^msgstr\[[0-9]+\] ")
	products = []
	with open(path, "r") as f:
		while True:
			entry = {}
			key = None
			parameters = {}
			is_complete = False
			for l in f:
				if l.startswith("\""):
					# multi-line string
					entry[key] += ast.literal_eval(l.strip())
				elif plural_regex.match(l):
					key = l[:9]
					entry[key] = ast.literal_eval(l[10:].strip())
					is_complete = True
				elif is_complete:
					break
				elif l.startswith("msgctxt "):
					key = "msgctxt"
					entry[key] = ast.literal_eval(l[7:].strip())
				elif l.startswith("msgid "):
					key = "msgid"
					entry[key] = ast.literal_eval(l[5:].strip())
				elif l.startswith("msgid_plural "):
					key = "msgid_plural"
					entry[key] = ast.literal_eval(l[12:].strip())
				elif l.startswith("msgstr "):
					key = "msgstr"
					entry[key] = ast.literal_eval(l[6:].strip())
					is_complete = True
				elif l.startswith("#"):
					parameter_m = parameter_regex.match(l)
					if parameter_m:
						# parameter line
						parameters[parameter_m.group(1)] = parameter_m.group(2)

			if not entry:
				return products
			if parameters:
				entry["parameters"] = parameters
			products += [entry]
	return products

class _Po2Arb:
	def __call__(self, po):
		arb = {}
		for entry in po:
			if not entry["msgid"]:
				# header entry, ignore
				continue
			if "msgstr" in entry:
				string = entry["msgstr"]
				if "parameters" in entry:
					for key, value in entry["parameters"].items():
						string = string.replace(f"%{key}$s", f"{{{value}}}")
			elif "msgstr[0]" in entry:
				# plural
				var = next(iter(entry["parameters"].values()))
				pattern_str = ""
				for i in range(4):
					item = entry[f"msgstr[{i}]"]
					if item:
						# escape ' and sharp
						item = item.replace("'", "''")
						item = item.replace("#", "'#'")
						for p_i, (key, value) in enumerate(
								entry["parameters"].items()):
							# somehow flutter doesn't support #. oops
							# item = item.replace(f"%{key}$s",
							# 	f"{{{value}}}" if p_i > 0 else "#")
							item = item.replace(f"%{key}$s", f"{{{value}}}")
						if i == 3:
							category = "other"
						else:
							category = f"={i}"
						pattern_str += f"{category} {{{item}}} "
				if pattern_str:
					string = f"{{{var}, plural, {pattern_str.strip()}}}"
				else:
					# untranslated
					string = ""

			if string:
				#translated entry
				arb[entry["msgctxt"]] = string
				if "parameters" in entry:
					arb["@" + entry["msgctxt"]] = {
						"placeholders": {key: {} for key
							in entry["parameters"].values()}
					}
		return arb

def po2arb(file, json_indent=2):
	po = _parse_po(file)
	return json.dumps(_Po2Arb()(po), indent=json_indent, ensure_ascii=False)

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(
		description="Convert a gettext PO file back to ARB file. Notice that this only works if the PO file was originally converted by us from an ARB file",
	)
	parser.add_argument(
		"po",
	)
	_args = parser.parse_args()
	print(po2arb(_args.po))
