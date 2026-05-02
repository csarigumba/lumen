#!/usr/bin/env bash
# Extract every link from content/posts/**/index.md.
# Output: <file>:<line>\t<url>
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Use perl for portable regex with captures (works on macOS without gawk).
find content/posts -name 'index.md' -print0 \
  | while IFS= read -r -d '' file; do
      perl -ne '
        my $line = $.;
        my $f = $ARGV;
        # Markdown links and images: [text](url) or ![alt](url)
        while (/!?\[[^\]]*\]\(([^) ]+)\)/g) {
          print "$f:$line\t$1\n";
        }
        # Reference style: [id]: url
        if (/^\[[^\]]+\]:\s+(\S+)/) {
          print "$f:$line\t$1\n";
        }
        # Bare URLs not already inside markdown wrap
        while (/(?<![\(\[])\b(https?:\/\/[^\s<>")\]]+)/g) {
          print "$f:$line\t$1\n";
        }
      ' "$file"
    done \
  | sort -u
