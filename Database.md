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

* Hanzi in the database are bounded. That is, only a subset of Unicode CJK Unified Ideographs are to be listed. To begin with, only the 6500 common (level 1 & 2) Hanzi listed in the [Tongyong Guifan Hanzi Biao](https://en.wikipedia.org/wiki/Table_of_General_Standard_Chinese_Characters) (abbr. *Zibiao* hereinafter), along with other necessary Hanzi characters or components to link them together, are planned to be included. Later development may expand to the full set in the Table, and / or [IICore](https://en.wikipedia.org/wiki/International_Ideographs_Core).

## Concepts

* Separate the graphemes from the morphemes of Hanzi into two tables, one for orthography and general hierarchy, and the other for pronunciations and phonetic / cognition links.
	* These two tables are named `HZGraph` and `HZMorph` respectively.
* Column names follow [Hungarian notation](https://en.wikipedia.org/wiki/Hungarian_notation), and use abbreviations and acronyms to make them no longer than 8 alphabets.
  Prefixes to be used:
	* `b` for Boolean
	* `n` for Numeric / Integer
	* `t` for Text

## Schema

### HZGraph

| Column     | Description                                                     |
| :-----:    | :-------------------------------------------------------------- |
| `tHanzi`   | Hanzi in UTF-8 text (same applies hereinafter) as the primary key |
| `tParent`  | Nullable parent Hanzi in general hierarchy, usually the proper form or phonetic component |
| `tSimp`    | Non-null space-delimited Simplified Chinese forms |
| `tGBFB`    | GB2312 fallback character (sequence) |
| `tTrad`    | Non-null space-delimited Traditional Chinese forms |
| `tB5FB`    | BIG5 fallback character (sequence) |
| `tJpShin`  | Non-null space-delimited Japanese Shinjitai (new character style) forms |
| `tJISFB`   | JIS X 0208 fallback character (sequence) |

### HZMorph

| Column     | Description                                                     |
| :-----:    | :-------------------------------------------------------------- |
| `tHZ`      | Hanzi text. Together with `tPY` and `tMGCR` the primary key is formed |
| `tPY`      | Pinyin in plain ASCII (suffix 1 to 5 for tone markers, v for ü) |
| `tMGCR`    | Modified General Chinese Romanization |
| `nFreq`    | Frequency of this reading according to `kHanyuPinlu` from Unihan DB (excluding non-proper Hanzi), 7 for level 1 in *Zibiao*, 6 for priority A in IICore, 5 for level 2, 4 for priority B, 3 for level 3, 2 for priority C, 1 for other entries found in dictionaries, 0 for artificial readings |
| `bInGY`    | Whether this reading is derived from an entry in the MC rhyme book [Guangyun](https://en.wikipedia.org/wiki/Guangyun) |
| `tPhon`    | Phonetic component if any |
| `tVar1`    | Space-delimited Type-1 variants, which can be exchanged without ambiguity |
| `tVar2`    | Space-delimited Type-2 variants, which can be exchanged only in some cases of specific meanings |
| `tVar3`    | Space-delimited Type-3 variants, which cannot be exchanged, usually a phonetic loan |
| `tCogn`    | Space-delimited cognate characters if any |
| `tCoin`    | Original characters of the coinage if any |
| `tRem`     | Optional remark of this entry |
