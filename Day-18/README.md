# Day 18: Regular Expressions (Regex)

Everything is in one notebook: `Day18_Regex.ipynb` (run top to bottom; needs `pandas`).

## What's inside

| Deliverable | Location in notebook |
|---|---|
| 20+ regex patterns | Section 4: 22 patterns, each auto-tested with a valid and invalid example |
| Data cleaning scripts | Sections 5 and 6.1: phones, emails, dates, names, text |
| Pattern library | `PATTERNS` dict + `is_valid(kind, value)` helper |
| Log parser | Section 6.2: Apache-style access log and app log into DataFrames |
| Regex guide | This file |

---

## Regex Guide

### 1. Basics

| Piece | Syntax | Example | Matches |
|---|---|---|---|
| Literal | `cat` | `cat` | "cat" |
| Any char | `.` | `c.t` | cat, cot, c-t |
| Digit / non-digit | `\d` / `\D` | `\d+` | 123 |
| Word char / non-word | `\w` / `\W` | `\w+` | hello_1 |
| Whitespace | `\s` / `\S` | `\s+` | spaces, tabs |
| Escape | `\.` | `\d+\.\d+` | 9.99 |
| OR | `a\|b` | `cat\|dog` | cat or dog |

**Character classes:** `[aeiou]` (any vowel), `[A-Z]` (range), `[^0-9]` (NOT digits)

**Quantifiers**

| Symbol | Meaning |
|---|---|
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 (optional) |
| `{n}` | exactly n |
| `{n,m}` | n to m |
| `+?` `*?` | lazy (match as little as possible) |

**Anchors:** `^` start, `$` end, `\b` word boundary

**Groups**

| Syntax | Use |
|---|---|
| `( )` | capture |
| `(?: )` | group without capturing |
| `(?P<name> )` | named group, read with `m.group("name")` |
| `\1`, `\2` | backreferences (in `re.sub`) |
| `(?= )` | lookahead (used in the password pattern) |

### 2. The `re` module

| Function | Purpose | Returns |
|---|---|---|
| `re.search(p, s)` | first match anywhere | match or `None` |
| `re.match(p, s)` | match at the start only | match or `None` |
| `re.findall(p, s)` | all matches | list |
| `re.sub(p, repl, s)` | replace matches | string |
| `re.compile(p)` | pre-build a reusable pattern | pattern object |

**Flags:** `re.I` ignore case, `re.M` multiline `^ $`, `re.S` dot matches newline, `re.X` verbose (comments allowed)

### 3. Pattern library

`email`, `phone_us`, `phone_intl`, `url`, `ipv4`, `mac_address`, `date_iso`, `date_us`, `date_dmy`, `time_24h`, `zip_us`, `pin_india`, `hex_color`, `uuid`, `username`, `strong_password`, `credit_card`, `ssn`, `currency`, `hashtag`, `mention`, `html_tag`, `only_digits`

```python
is_valid("email", "me@site.com")   # True
is_valid("ipv4", "300.1.1.1")      # False
```

### 4. Cleaning recipes

```python
re.sub(r"\D", "", phone)            # keep digits only
re.sub(r"\s+", " ", text).strip()   # collapse extra spaces
re.sub(r"[^A-Za-z0-9\s]", "", text) # remove special characters
re.sub(r"<[^>]+>", "", html)        # strip HTML tags
re.findall(r"[\w.+-]+@[\w.-]+\.\w+", text)   # extract emails
```
