#!/usr/bin/env python3
import tempfile
import unittest
from arb2po import arb2po

_HEADER = r"""
msgid ""
msgstr ""
"Plural-Forms: nplurals=4; plural=n == 0 ? 0 : n == 1 ? 1 : n == 2 ? 2 : 3;"
""".strip()

class TestArb2Po(unittest.TestCase):
	def test_header(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write("{}")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(), _HEADER)

	def test_basic(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "bar"
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#, no-c-format
msgctxt "foo"
msgid "bar"
msgstr ""
""".rstrip())

	def test_decription(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "bar",
	"@foo": {
		"description": "hello world"
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. hello world
#, no-c-format
msgctxt "foo"
msgid "bar"
msgstr ""
""".rstrip())

	def test_one_parameter(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param} bar",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "%1$s bar"
msgstr ""
""".rstrip())

	def test_two_parameters(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param1} bar {param2}",
	"@foo": {
		"placeholders": {
			"param1": {},
			"param2": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param1
#. Parameter 2: param2
#, c-format
msgctxt "foo"
msgid "%1$s bar %2$s"
msgstr ""
""".rstrip())

	def test_parameter_example(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param} bar",
	"@foo": {
		"placeholders": {
			"param": {
				"example": "hello"
			}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param (example: hello)
#, c-format
msgctxt "foo"
msgid "%1$s bar"
msgstr ""
""".rstrip())

	def test_newline_character(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "bar\nbar"
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#, no-c-format
msgctxt "foo"
msgid "bar\nbar"
msgstr ""
""".rstrip())

	def test_escape(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "bar\\bar"
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#, no-c-format
msgctxt "foo"
msgid "bar\\bar"
msgstr ""
""".rstrip())

	def test_plural_basic(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_plural_one_parameter(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{{param} plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "%1$s plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_plural_one_parameter_sharp(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{# plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "%1$s plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_plural_zero(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =0{none} =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
#. If zero: "none"
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_plural_no_one(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "plural"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_plural_escape_sharp(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{'#' plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "# plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_plural_escape_apostrophes(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{'' plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()
		out = arb2po(f.name, None)
		f.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "' plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_translated_basic(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "bar"
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "translated"
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#, no-c-format
msgctxt "foo"
msgid "bar"
msgstr "translated"
""".rstrip())

	def test_translated_one_parameter(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param} bar",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param} translated",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "%1$s bar"
msgstr "%1$s translated"
""".rstrip())

	def test_translated_two_parameters(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param1} bar {param2}",
	"@foo": {
		"placeholders": {
			"param1": {},
			"param2": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param1} translated {param2}",
	"@foo": {
		"placeholders": {
			"param1": {},
			"param2": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param1
#. Parameter 2: param2
#, c-format
msgctxt "foo"
msgid "%1$s bar %2$s"
msgstr "%1$s translated %2$s"
""".rstrip())

	def test_translated_two_parameters_swapped(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param1} bar {param2}",
	"@foo": {
		"placeholders": {
			"param1": {},
			"param2": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param2} translated {param1}",
	"@foo": {
		"placeholders": {
			"param1": {},
			"param2": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param1
#. Parameter 2: param2
#, c-format
msgctxt "foo"
msgid "%1$s bar %2$s"
msgstr "%2$s translated %1$s"
""".rstrip())

	def test_translated_plural_basic_zero(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param, plural, =0{zero}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] "zero"
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_translated_plural_basic_zero_textual(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param, plural, zero{0}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] "0"
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_translated_plural_basic_one(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param, plural, =1{one}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] "one"
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_translated_plural_basic_one_textual(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param, plural, one{1}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] "1"
msgstr[2] ""
msgstr[3] ""
""".rstrip())

	def test_translated_plural_basic_two(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param, plural, =2{two}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] "two"
msgstr[3] ""
""".rstrip())

	def test_translated_plural_basic_two_textual(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param, plural, two{2}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] "2"
msgstr[3] ""
""".rstrip())

	def test_translated_plural_basic_other(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param, plural, other{many}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] "many"
""".rstrip())

	def test_translated_plural_one_parameter(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "{param, plural, =1{singular} other{{param} plural}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "{param, plural, =0{zero {param}} =1{one {param}} =2{two {param}} other{many {param}}}",
	"@foo": {
		"placeholders": {
			"param": {}
		}
	}
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "%1$s plural"
msgstr[0] "zero %1$s"
msgstr[1] "one %1$s"
msgstr[2] "two %1$s"
msgstr[3] "many %1$s"
""".rstrip())

	def test_translated_unicode(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
{
	"foo": "bar"
}
""")
		f.flush()

		tf = tempfile.NamedTemporaryFile(mode="w+")
		tf.write(
r"""
{
	"foo": "★"
}
""")
		tf.flush()

		out = arb2po(f.name, tf.name)
		f.close()
		tf.close()
		self.assertEqual(out.strip(),
_HEADER + r"""

#, no-c-format
msgctxt "foo"
msgid "bar"
msgstr "★"
""".rstrip())

if __name__ == "__main__":
    unittest.main()
