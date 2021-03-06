# arb2po

[![pipeline status](https://gitlab.com/nkming2/arb2po/badges/master/pipeline.svg)](https://gitlab.com/nkming2/arb2po/-/commits/master) 

Convert ARB file to PO file

ARB format is being used in flutter intl package but tooling support for it is
minimal. This <s>hackish</s> script can convert it to the more popular gettext
PO format for localization work

## Compatibility
* plural is partially supported (see [Warning](#Warning))
* gender is not supported

## Usage
```
arb2po.py SRC_ARB [LOCALIZED_ARB]
```
* SRC_ARB
	* The untranslated ARB file
* LOCALIZED_ARB
	* Localized ARB file. If available, the resulting PO file will contain
	translated string from this file


```
po2arb.py PO
```
* PO
	* The translated PO file

### Example
```
arb2po.py app_en.arb app_es.arb > es.po
po2arb.py es.po > app_es.arb
```

## Warning
As mentioned, this script is pretty hackish, so beware of the following
limitations:
* plural is supported when the whole string is inside the plural block but not
when used inline
	* Supported: "{p, plural, =1{some a text} other{some b text}}"
	* **NOT** supported: "some {p, plural, =1{a} other{b}} text"
* There will always be 4 msgstr for plural, namely zero, one, two and other.
Leave the string empty for those not applicable to your language
	* The 4 msgstr translate to =0{}, =1{}, =2{}, other{} respectively in ARB
	* For example, you would leave msgstr[0] and msgstr[2] empty for English
	* It's useless to change the Plural-Forms header, we don't read that
* PO file generated by arb2po does conform to the spec but the content is
unusual
	* You may receive warnings from your tools
* po2arb **ONLY** supports converting a PO file created by arb2po
	* Don't feed a native PO file and expecting it to work. It won't
