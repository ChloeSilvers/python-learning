import re

def format_receipt(items, prices, quantities):
    width = 39                
    sep = "=" * width
    header = f"{'Item':<20}{'Qty':^5}{'Price':>14}"
    lines = [sep, header, sep]
    total = 0.0
    for item, price, qty in zip(items, prices, quantities):
        line_total = price * qty
        total += line_total
        price_str = f"$ {line_total:6.2f}"
        lines.append(f"{item:<20}{str(qty):^5}{price_str:>14}")
    lines.append(sep)
    total_str = f"$ {total:6.2f}"
    lines.append(f"{'TOTAL':<20}{'':^5}{total_str:>14}")
    lines.append(sep)
    return "\n".join(lines)

def process_user_data(raw_data):
    name_raw = raw_data.get('name','')
    name = ' '.join(name_raw.strip().split()).title()
    email_raw = raw_data.get('email','')
    email = email_raw.strip().lower().replace(' ', '')
    phone_raw = raw_data.get('phone','')
    phone = re.sub(r'\D', '', phone_raw)   
    address_raw = raw_data.get('address','')
    address = ' '.join(address_raw.strip().split()).title()
    username = '_'.join(name.lower().split())
    email_valid = bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))
    phone_valid = len(phone) >= 10
    return {
        'name': name,
        'email': email,
        'phone': phone,
        'address': address,
        'username': username,
        'validation': {'email_valid': email_valid, 'phone_valid': phone_valid}
    }

def analyze_text(text):
    total_chars = len(text)
    lines = text.splitlines()
    total_lines = len(lines)
    words = re.findall(r'\b\w+\b', text)
    total_words = len(words)
    avg_word_length = round(sum(len(w) for w in words)/total_words, 2) if total_words else 0.0
    freq = {}
    for w in map(str.lower, words):
        freq[w] = freq.get(w, 0) + 1
    most_common_word = max(freq, key=freq.get) if freq else ''
    longest_line = max(lines, key=len) if lines else ''
    words_per_line = [len(re.findall(r'\b\w+\b', ln)) for ln in lines]
    sentences = re.findall(r'[^.!?]+[.!?]', text, flags=re.S)
    capitalized_sentences = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
    questions = sum(1 for s in sentences if s.strip().endswith('?'))
    exclamations = sum(1 for s in sentences if s.strip().endswith('!'))
    return {
        'total_chars': total_chars,
        'total_words': total_words,
        'total_lines': total_lines,
        'avg_word_length': avg_word_length,
        'most_common_word': most_common_word,
        'longest_line': longest_line,
        'words_per_line': words_per_line,
        'capitalized_sentences': capitalized_sentences,
        'questions': questions,
        'exclamations': exclamations
    }

def find_patterns(text):
    decimals = re.findall(r'\b\d+\.\d+\b', text)
    integers = re.findall(r'\b\d+\b', re.sub(r'\b\d+\.\d+\b', ' ', text))
    words_with_digits = re.findall(r'\b\w*\d\w*\b', text)
    capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)
    all_caps_words = re.findall(r'\b[A-Z]{2,}\b', text)
    repeated_words = [m.group(0) for m in re.finditer(r'\b\w*([A-Za-z0-9])\1\w*\b', text)]
    return {
       'integers': integers,
       'decimals': decimals,
       'words_with_digits': words_with_digits,
       'capitalized_words': capitalized_words,
       'all_caps_words': all_caps_words,
       'repeated_chars': repeated_words
    }

def validate_format(input_string, format_type):
    patterns = {
        'phone': r'^(?:\((?P<area>\d{3})\)\s*(?P<prefix>\d{3})-(?P<line>\d{4})|(?P<area2>\d{3})-(?P<prefix2>\d{3})-(?P<line2>\d{4}))$',
        'date': r'^(?P<month>0[1-9]|1[0-2])/(?P<day>0[1-9]|[12][0-9]|3[01])/(?P<year>(19|20)\d{2})$',
        'time': r'^(?P<hour>(0[0-9]|1[0-9]|2[0-3]|0[1-9]|1[0-2])):(?P<minute>[0-5][0-9])(?:\s*(?P<ampm>(AM|PM|am|pm)))?$',
        'email': r'^(?P<user>[\w\.-]+)@(?P<domain>[\w\.-]+\.\w+)$',
        'url': r'^(?P<proto>https?)://(?P<host>[\w\.-]+(?:\.[\w\.-]+)+)(?P<path>/.*)?$',
        'ssn': r'^(?P<part1>\d{3})-(?P<part2>\d{2})-(?P<part3>\d{4})$'
    }
    pattern = patterns.get(format_type)
    if not pattern:
        return (False, None)
    match = re.match(pattern, input_string)
    if not match:
        return (False, None)
    parts = {k: v for k, v in match.groupdict().items() if v is not None}
    if format_type == 'phone':
        if 'area2' in parts:
            parts['area'] = parts.pop('area2')
            parts['prefix'] = parts.pop('prefix2')
            parts['line'] = parts.pop('line2')
        parts = {'area_code': parts.get('area'), 'prefix': parts.get('prefix'), 'line': parts.get('line')}
    return (True, parts)

def extract_information(text):
    prices = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', text)
    percentages = re.findall(r'\b\d+(?:\.\d+)?%', text)
    years = re.findall(r'\b(?:19|20)\d{2}\b', text)
    sentences = re.findall(r'[^.!?]+[.!?]', text, flags=re.S)
    questions = [s.strip() for s in sentences if s.strip().endswith('?')]
    quoted = re.findall(r'"(.*?)"', text, flags=re.S)
    return {'prices': prices, 'percentages': percentages, 'years': years,
            'sentences': [s.strip() for s in sentences], 'questions': questions, 'quoted_text': quoted}

def analyze_log_file(log_text):
    log_pattern = re.compile(
        r'^\[(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\]\s+(?P<level>\w+):\s*(?P<msg>.*)$',
        flags=re.M
    )
    entries = log_pattern.findall(log_text)
    total_entries = len(entries)
    level_counts = {}
    for _, _, level, _ in entries:
        level_counts[level] = level_counts.get(level, 0) + 1
    unique_dates = sorted(set(date for date, _, _, _ in entries))
    error_messages = [msg for _, _, level, msg in entries if level == 'ERROR']
    times = [time for _, time, _, _ in entries]
    time_range = (min(times), max(times)) if times else (None, None)
    hours = [t[:2] for t in times]
    hour_counts = {}
    for h in hours:
        hour_counts[h] = hour_counts.get(h, 0) + 1
    most_active_hour = max(hour_counts, key=hour_counts.get) if hour_counts else None
    return {
        'total_entries': total_entries,
        'level_counts': level_counts,
        'unique_dates': unique_dates,
        'error_messages': error_messages,
        'time_range': time_range,
        'most_active_hour': most_active_hour
    }

def clean_text_pipeline(text, operations):
    steps = [text]
    s = text
    for op in operations:
        if op == 'trim':
            s = s.strip()
        elif op == 'lowercase':
            s = s.lower()
        elif op == 'remove_punctuation':
            s = re.sub(r'[^\w\s]', '', s)
        elif op == 'remove_digits':
            s = re.sub(r'\d+', '', s)
        elif op == 'remove_extra_spaces':
            s = re.sub(r'\s+', ' ', s).strip()
        elif op == 'remove_urls':
            s = re.sub(r'https?://\S+', '', s)
        elif op == 'remove_emails':
            s = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', s)
        elif op == 'capitalize_sentences':
            parts = re.split(r'([.!?])', s)
            new_parts = []
            for i in range(0, len(parts), 2):
                sentence = parts[i].strip()
                if not sentence:
                    continue
                punct = parts[i + 1] if i + 1 < len(parts) else ''
                sentence = sentence[0].upper() + sentence[1:] if sentence else ''
                new_parts.append(sentence + punct)
            s = ' '.join(new_parts).strip()
        steps.append(s)
    return {'original': text, 'cleaned': s, 'steps': steps}

def smart_replace(text, replacements):
    s = text
    if replacements.get('censor_phone'):
        s = re.sub(r'\d{3}-\d{3}-\d{4}', 'XXX-XXX-XXXX', s)
    if replacements.get('censor_email'):
        s = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', s)
    if replacements.get('fix_spacing'):
        s = re.sub(r'\s*([,.!?])\s*', r'\1 ', s)
        s = re.sub(r'\s+', ' ', s).strip()
    if 'expand_contractions' in replacements:
        for contr, full in replacements['expand_contractions'].items():
            s = re.sub(r"\b" + re.escape(contr) + r"\b", full, s, flags=re.I)
    if replacements.get('number_to_word'):
        number_words = {
            "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
            "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"
        }
        for num, word in number_words.items():
            s = re.sub(r'\b' + num + r'\b', word, s)
    return s

def run_tests():
    print("Part 1:")
    items = ["Apples", "Bananas", "Milk"]
    prices = [0.5, 0.3, 2.0]
    quantities = [4, 6, 1]
    print("\nReceipt Example:")
    print(format_receipt(items, prices, quantities))
    raw_data = {
        'name': '   jOhN   doe ',
        'email': '  John.DOE @Example.com ',
        'phone': '(123) 456-7890',
        'address': '123 main st,  apartment 4B '
    }
    print("\nProcessed User Data:")
    print(process_user_data(raw_data))
    sample_text = """Hello World!
This is a test. How many words are here?
Python is great!"""
    print("\nText Analysis:")
    print(analyze_text(sample_text))
    print("\nPart 2:")
    pattern_text = "The price is 45.67 dollars, ID A123, CODE ABC, SHOUT WOW, year 2025!!"
    print("\nFound Patterns:")
    print(find_patterns(pattern_text))
    print("\nValidate Formats:")
    print("Phone:", validate_format("(123) 456-7890", "phone"))
    print("Date:", validate_format("12/25/2024", "date"))
    print("Time (12h):", validate_format("11:59 PM", "time"))
    print("Time (24h):", validate_format("23:59", "time"))
    print("Email:", validate_format("user@example.com", "email"))
    print("URL:", validate_format("https://www.example.com/path", "url"))
    print("SSN:", validate_format("123-45-6789", "ssn"))
    info_text = 'In 2023, revenue was $1,200.50 (up 10%). "Growth was amazing!" said the CEO. What next?'
    print("\nExtracted Information:")
    print(extract_information(info_text))
    print("\nPart 3:")
    messy = "   This is a   TEST!!! Visit https://example.com or email test@ex.com   "
    ops = ['trim', 'lowercase', 'remove_punctuation', 'remove_urls', 'remove_emails', 'remove_extra_spaces']
    print("\nCleaned Text Pipeline:")
    print(clean_text_pipeline(messy, ops))
    replace_text = "Call me at 123-456-7890 or email me@example.com. i can't go, it's late. I have 2 cats."
    replacements = {
        'censor_phone': True,
        'censor_email': True,
        'fix_spacing': True,
        'expand_contractions': {
            "can't": "cannot",
            "it's": "it is"
        },
        'number_to_word': True
    }
    print("\nSmart Replace:")
    print(smart_replace(replace_text, replacements))
    print("\nPart 4:")
    log_sample = """[2025-09-28 14:05:23] INFO: System started
[2025-09-28 14:06:10] ERROR: Disk not found
[2025-09-28 15:15:45] WARNING: Low memory
[2025-09-29 09:00:00] INFO: User login"""
    print("\nLog Analysis:")
    print(analyze_log_file(log_sample))

if __name__ == "__main__":
    run_tests()
