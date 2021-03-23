#!/usr/bin/env python3
import tempfile
import unittest
from po2arb import po2arb

class TestPo2Arb(unittest.TestCase):
	def test_empty(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(), "{}")

	def test_header(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
msgid ""
msgstr ""
"Plural-Forms: nplurals=4; plural=n == 0 ? 0 : n == 1 ? 1 : n == 2 ? 2 : 3;"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(), "{}")

	def test_untranslated(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#, no-c-format
msgctxt "foo"
msgid "untranslated"
msgstr ""
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(), "{}")

	def test_basic(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#, no-c-format
msgctxt "foo"
msgid "untranslated"
msgstr "bar"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "bar"
}
""".strip())

	def test_one_parameter(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "untranslated %1$s"
msgstr "bar %1$s"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "bar {param}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_two_parameters(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param1
#. Parameter 2: param2
#, c-format
msgctxt "foo"
msgid "%1$s untranslated %2$s"
msgstr "%1$s bar %2$s"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
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
""".strip())

	def test_two_parameters_swapped(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param1
#. Parameter 2: param2
#, c-format
msgctxt "foo"
msgid "%1$s untranslated %2$s"
msgstr "%2$s bar %1$s"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "{param2} bar {param1}",
  "@foo": {
    "placeholders": {
      "param1": {},
      "param2": {}
    }
  }
}
""".strip())

	def test_parameter_example(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param (example: 1)
#, c-format
msgctxt "foo"
msgid "untranslated %1$s"
msgstr "bar %1$s"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "bar {param}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_newline_character(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#, no-c-format
msgctxt "foo"
msgid "untranslated\nline"
msgstr "bar\nbar"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "bar\nbar"
}
""".strip())

	def test_plural_untranslated(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(), "{}")

	def test_plural_basic(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] "bar"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "{param, plural, other {bar}}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_plural_one_parameter(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "%1$s plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] "%1$s bar"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "{param, plural, other {{param} bar}}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_plural_escape_sharp(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] "bar#"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "{param, plural, other {bar'#'}}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_plural_escape_apostrophes(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
msgstr[3] "bar'"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "{param, plural, other {bar''}}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_translated_plural_basic_zero(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] "bar"
msgstr[1] ""
msgstr[2] ""
msgstr[3] ""
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "{param, plural, =0 {bar}}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_translated_plural_basic_one(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] "bar"
msgstr[2] ""
msgstr[3] ""
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "{param, plural, =1 {bar}}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_translated_plural_basic_two(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#. Parameter 1: param
#, c-format
msgctxt "foo"
msgid "singular"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] "bar"
msgstr[3] ""
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "{param, plural, =2 {bar}}",
  "@foo": {
    "placeholders": {
      "param": {}
    }
  }
}
""".strip())

	def test_translated_unicode(self):
		f = tempfile.NamedTemporaryFile(mode="w+")
		f.write(
r"""
#, no-c-format
msgctxt "foo"
msgid "singular"
msgstr "★"
""")
		f.flush()
		out = po2arb(f.name)
		f.close()
		self.assertEqual(out.strip(),
r"""
{
  "foo": "★"
}
""".strip())

if __name__ == "__main__":
    unittest.main()
