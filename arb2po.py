#!/usr/bin/env python3
import json
import re

# Read and transform an .arb file to something easier to work with
def _parse_arb(path):
	product = {}
	with open(path, "r") as f:
		raw = json.load(f)
		for key, value in raw.items():
			if key.startswith("@"):
				# attributes
				continue
			product[key] = {
				"value": value,
			}
			if f"@{key}" in raw:
				# attributes available
				product[key]["attributes"] = raw[f"@{key}"]
	return product

class _Arb2Po:
	_PLURAL_REGEX = re.compile(r"^\{.+, *plural, .+\}$")
	_ICU_ESCAPE_APOSTROPHES_REGEX = re.compile(r"([^']|^)'")

	def __call__(self, original, translated):
		# headers
		yield "msgid \"\""
		yield "msgstr \"\""
		# Map:
		# 	=0/zero => msgstr[0]
		# 	=1/one => msgstr[1]
		# 	=2/two => msgstr[2]
		#	other => msgstr[3]
		yield "\"Plural-Forms: nplurals=4; plural=n == 0 ? 0 : n == 1 ? 1 : n == 2 ? 2 : 3;\""

		for o_key, o_value in original.items():
			yield ""
			t_value = translated[o_key] if o_key in translated else {}
			o_placeholders = {}
			try:
				t_placeholders = t_value["attributes"]["placeholders"]
			except KeyError:
				t_placeholders = {}
			# yield f"#: {o_key}"
			if "attributes" in o_value:
				try:
					o_placeholders = o_value["attributes"]["placeholders"]
				except:
					None
				if "description" in o_value["attributes"]:
					yield f"#. {o_value['attributes']['description']}"
				if o_placeholders:
					for i, (op_key, op_value) in enumerate(o_placeholders.items()):
						string = f"#. Parameter {i + 1}: {op_key}"
						if "example" in op_value:
							string += f" (example: {op_value['example']})"
						yield string
					yield "#, c-format"

			if not o_placeholders:
				yield "#, no-c-format"

			if o_placeholders and self._is_plural_string(o_value["value"]):
				o_plural = self._extract_plural_patterns(o_value["value"])
				_, o_patterns = o_plural["var"], o_plural["patterns"]
				try:
					t_plural = self._extract_plural_patterns(t_value["value"])
					_, t_patterns = t_plural["var"], t_plural["patterns"]
				except KeyError:
					t_patterns = {}

				try:
					o_zero = (o_patterns["=0"] if "=0" in o_patterns
						else o_patterns["zero"])
					# rule for zero exists
					yield f"#. If zero: \"{o_zero}\""
				except KeyError:
					t_str0 = ""
				yield f"msgctxt \"{o_key}\"!"

				try:
					o_one = (o_patterns["=1"] if "=1" in o_patterns
						else o_patterns["one"])
					o_id = self._prep_value(o_one, o_placeholders,
						is_plural_string=True)
				except KeyError:
					# use other{} then
					o_id = ""
				o_other = o_patterns["other"]
				o_id_plural = self._prep_value(o_other, o_placeholders,
					is_plural_string=True)

				if o_id:
					yield f"msgid \"{o_id}\""
				else:
					yield f"msgid \"{o_id_plural}\""
				yield f"msgid_plural \"{o_id_plural}\""

				try:
					t_zero = (t_patterns["=0"] if "=0" in t_patterns
						else t_patterns["zero"])
					t_str0 = self._prep_value(t_zero, t_placeholders,
						is_plural_string=True)
				except KeyError:
					t_str0 = ""
				yield f"msgstr[0] \"{t_str0}\""

				try:
					t_one = (t_patterns["=1"] if "=1" in t_patterns
						else t_patterns["one"])
					t_str1 = self._prep_value(t_one, t_placeholders,
						is_plural_string=True)
				except KeyError:
					t_str1 = ""
				yield f"msgstr[1] \"{t_str1}\""

				try:
					t_two = (t_patterns["=2"] if "=2" in t_patterns
						else t_patterns["two"])
					t_str2 = self._prep_value(t_two, t_placeholders,
						is_plural_string=True)
				except KeyError:
					t_str2 = ""
				yield f"msgstr[2] \"{t_str2}\""

				try:
					t_other = t_patterns["other"]
					t_str3 = self._prep_value(t_other, t_placeholders,
						is_plural_string=True)
				except KeyError:
					t_str3 = ""
				yield f"msgstr[3] \"{t_str3}\""
			else:
				yield f"msgctxt \"{o_key}\""
				yield f"msgid \"{self._prep_value(o_value['value'], o_placeholders)}\""
				try:
					yield f"msgstr \"{self._prep_value(t_value['value'], t_placeholders)}\""
				except KeyError:
					yield f"msgstr \"\""

	@staticmethod
	def _is_plural_string(s):
		return _Arb2Po._PLURAL_REGEX.match(s)

	# Search the matching closing bracket and return the closing index and the
	# string in-between
	@staticmethod
	def _extract_bracket(s):
		if not s.startswith("{"):
			raise ValueError(f"string not beginning with {{: {s}")
		nest = 0
		for i, c in enumerate(s):
			if c == "{":
				nest += 1
			elif c == "}":
				nest -= 1
				if nest == 0:
					return i, s[0 + 1:i]
		raise ValueError(f"Unbalanced bracket: {s}")

	# Search the first plural pattern and return the ending index and the
	# pattern
	#
	# Example: given "=0{zero}=1{one}..." return 7, ["=0", "zero"]
	@staticmethod
	def _extract_first_plural_pattern(s):
		begin = s.find("{")
		if begin == -1:
			raise ValueError(f"Missing open bracket: {s}")
		key = s[0:begin].strip()
		i, value = _Arb2Po._extract_bracket(s[begin:])
		return i + begin, [key, value]

	# Extract the plural patterns
	#
	# Example: given "{count, plural, =0{zero}=1{one}other{#}}" return
	# {"var": "count", "patterns": {"=0": "zero", "=1": "one", "other": "#"}}
	@staticmethod
	def _extract_plural_patterns(s):
		_, s = _Arb2Po._extract_bracket(s.strip())
		sections = s.split(",")
		var = sections[0].strip()
		if sections[1].strip() != "plural":
			raise ValueError("Not a plural string")
		product = {
			"var": var,
			"patterns": {}
		}
		plural_s = "".join(sections[2:]).strip()
		while plural_s:
			i, pattern = _Arb2Po._extract_first_plural_pattern(plural_s)
			product["patterns"][pattern[0]] = pattern[1]
			plural_s = plural_s[i + 1:]
		return product

	# Prepare a string value to be written
	@staticmethod
	def _prep_value(value, placeholders, is_plural_string=False):
		value_ = value
		if placeholders:
			value_ = _Arb2Po._transform_placeholders(value_, placeholders,
				allow_sharp=is_plural_string)
		value_ = _Arb2Po._escape_str(value_, is_icu=is_plural_string)
		return value_

	@staticmethod
	def _transform_placeholders(s, placeholders, allow_sharp=False):
		product = s
		for i, key in enumerate(placeholders.keys()):
			product = product.replace(f"{{{key}}}", f"%{i + 1}$s")
		if allow_sharp:
			find_i = -1
			while True:
				find_i = product.find("#", find_i + 1)
				if find_i == -1:
					break
				if product[:find_i].count("'") % 2 == 0:
					# even = not escaped
					product = product[:find_i] + "%1$s" + product[find_i + 1:]
					find_i += 4
		return product

	# Escape invalid characters in string, like [", \n]
	@staticmethod
	def _escape_str(s, is_icu=False):
		s = s.replace("\\", "\\\\")
		s = s.replace("\"", "\\\"")
		s = s.replace("\n", "\\n")
		if is_icu:
			s = _Arb2Po._ICU_ESCAPE_APOSTROPHES_REGEX.sub(r"\1", s)
		return s

def arb2po(untranslated_file, translated_file):
	original = _parse_arb(untranslated_file)
	if translated_file:
		translated = _parse_arb(translated_file)
	else:
		translated = {}
	return "\n".join(_Arb2Po()(original, translated))

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(
		description="Convert ARB file to something compatible with the gettext PO format",
	)
	parser.add_argument(
		"src_arb",
	)
	parser.add_argument(
		"localized_arb",
		nargs="?",
		help="Translated strings will be taken form this file if available"
	)
	_args = parser.parse_args()
	print(arb2po(_args.src_arb, _args.localized_arb))
