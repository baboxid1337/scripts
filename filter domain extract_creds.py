extract_creds.py
python3 extract_creds.py domain.txt output_clean.txt --dedup --sort --keep-empty-passwords false

#!/usr/bin/env python3 //Babox1337
"""
extract_creds.py
Parse messy lines and produce cleaned "domain:username:password" output.

Usage:
    python3 extract_creds.py input.txt output.txt [--dedup] [--sort] [--keep-empty-passwords true|false]

Behavior:
 - Extracts host from URLs (removes scheme, path, port, www.)
 - Accepts separators like ":" (colon) primarily; falls back to whitespace splits
 - Trims whitespace around fields
 - Outputs domain:username:password
 - Options: deduplicate, sort, keep empty passwords
"""

import sys
import re
from urllib.parse import urlparse
import argparse

def extract_host(token):
    token = token.strip()
    if not token:
        return ''
    # If it contains space and likely multiple tokens, just return token (caller will handle)
    # Ensure a scheme for urlparse
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', token):
        token_for_parse = 'http://' + token
    else:
        token_for_parse = token
    try:
        p = urlparse(token_for_parse)
        host = p.netloc or p.path
        # remove trailing slashes or paths that might end up in path
        host = host.split('/')[0]
        # remove credentials@ if present
        if '@' in host:
            host = host.split('@')[-1]
        # strip port
        host = host.split(':')[0]
        # remove www.
        host = re.sub(r'^(www\.)', '', host, flags=re.I)
        return host.strip()
    except Exception:
        return token.strip()

def split_line(line):
    # Try safe colon-splitting first but allow more than 3 parts (password may contain colons).
    # Strategy: split into at most 3 parts: domain (left), username (middle), password (rest joined)
    line = line.strip()
    if not line:
        return None
    # Normalize unicode spaces
    line = re.sub(r'\s+', ' ', line)
    # First attempt: split on colon with optional surrounding spaces
    parts = re.split(r'\s*:\s*', line)
    if len(parts) >= 3:
        domain_raw = parts[0]
        username = parts[1]
        password = ':'.join(parts[2:])  # join the rest (password might contain :)
        return domain_raw, username, password
    # Fallback: split on whitespace into 3 parts
    parts_ws = line.split()
    if len(parts_ws) >= 3:
        domain_raw = parts_ws[0]
        username = parts_ws[1]
        password = ' '.join(parts_ws[2:])
        return domain_raw, username, password
    # If only 2 parts (domain:username) treat password empty
    if len(parts) == 2:
        return parts[0], parts[1], ''
    # single token: treat as domain only
    if len(parts) == 1:
        return parts[0], '', ''
    return None

def process_file(in_path, out_path, dedup=False, sort_out=False, keep_empty_passwords=False):
    results = []
    with open(in_path, 'r', encoding='utf-8', errors='ignore') as fi:
        for raw in fi:
            raw = raw.strip()
            if not raw:
                continue
            parsed = split_line(raw)
            if not parsed:
                continue
            domain_raw, username, password = parsed
            domain = extract_host(domain_raw)
            username = username.strip()
            password = password.strip()
            # Optionally skip entries without username or without password
            if username == '':
                # skip lines without username (they're not useful for your requested format)
                continue
            if password == '' and not keep_empty_passwords:
                # skip if no password and user didn't want empty-password entries
                continue
            results.append((domain, username, password))
    # dedup
    if dedup:
        seen = set()
        uniq = []
        for tup in results:
            key = f"{tup[0]}:{tup[1]}:{tup[2]}"
            if key not in seen:
                seen.add(key)
                uniq.append(tup)
        results = uniq
    # sort
    if sort_out:
        results.sort(key=lambda x: (x[0].lower(), x[1].lower()))
    # write output
    with open(out_path, 'w', encoding='utf-8') as fo:
        for domain, user, pw in results:
            fo.write(f"{domain}:{user}:{pw}\n")
    print(f"Done — wrote {len(results)} items to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Clean domain:username:password extractor")
    parser.add_argument('input', help='input file (domain.txt)')
    parser.add_argument('output', help='output file')
    parser.add_argument('--dedup', action='store_true', help='deduplicate results')
    parser.add_argument('--sort', dest='sort_out', action='store_true', help='sort results by domain then username')
    parser.add_argument('--keep-empty-passwords', dest='keep_empty_passwords', action='store_true',
                        help='keep entries with empty password')
    args = parser.parse_args()
    process_file(args.input, args.output, dedup=args.dedup, sort_out=args.sort_out, keep_empty_passwords=args.keep_empty_passwords)

if __name__ == '__main__':
    main()
