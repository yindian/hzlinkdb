# Database Design

## Disclaimer

This is an amateur project. The author's point of view may be unprofessional or far-fetched. Comments and corrections are appreciated. Use this database at your own risk!
 
## How to link Hanzi

* Alternatives or variants
	* E.g. 压/壓

* Same or similar pronunciations
	* In Mandarin / common dialects
	* E.g. 压/鸭

* Share the same phonetic components, regardless of pronunciation similarity
	* Sounds shift over time. Alterations in Old Chinese or Middle Chinese consonants / rhymes / tones
	* E.g. 压/厌 (厭 phonetic, different tones in MC)

* Cognates, which usually sound alike
	* E.g. 压/押/轧 (supposed to explain Cantonese / Japanese reading of *at*, not *ap*)

* Coinage of multiple Hanzi
	* E.g. 诸/之于, 呎/英尺

## What is this database for and not for

* Only for information needed to link Hanzi in ways described above
	* To lessen the burden on construction and maintenance

* Not a dictionary, glossary, nor rhyme book
	* Existing projects already play good roles. E.g. [Wiktionary](https://en.wiktionary.org), [Zdic.net](http://www.zdic.net), both of which contains explanations and modern / OC / MC readings of Hanzi.
	* There are many different notation systems for OC / MC, and some Hanzi in common contemporary dialects differ from their MC counterpart in sound, such as 鼻 (*-t* entering tone vs MC departing tone), 妈 (level tone vs MC rising tone), 打 (*-ng* coda lost). To make life easier, this database does not include OC / MC phonics, and instead utilizes a diasystem for modern Chinese. Among the related works such as [General Chinese](https://en.wikipedia.org/wiki/General_Chinese) by Yuen Ren Chao, [CDC](http://www.cssn.cn/yyx/yyx_fy/201505/t20150512_1776011.shtml) by Jerry Norman, etc., Chao's great work is chosen as the base, since it appears to be the most practical and resource-rich (such as the [digitized table of syllables](https://www.newsmth.net/bbscon.php?bid=203&id=78461)), with alterations in tonal spellings, to use more intuitive and popular *-x* and *-h* finals to indicate rising and departing tones, in lieu of the original Gwoyeu-Romatzyh-like system. The modified GCR is referred to as MGCR hereinafter.
	* Artificial / Hypothetical readings of Hanzi are also included in the database, to represent the deduced modern sounds (differ from actual) according to OC / MC, and thus to help clarify the links in phonetic series.

## Concepts

* Separate the graphemes from the morphemes of Hanzi into two tables, one for orthography and general hierarchy, and the other for pronunciations and phonetic / cognition links.
* Column names follow [Hungarian notation](https://en.wikipedia.org/wiki/Hungarian_notation), and use abbreviations and acronyms to make them no longer than 8 alphabets.

## Schema

