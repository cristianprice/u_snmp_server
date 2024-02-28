import os
import re

count = 0


def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""
    class K(object):
        __slots__ = ['obj']

        def __init__(self, obj):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        __hash__ = None
    return K


def _compile_pattern(pat):
    if isinstance(pat, bytes):
        pat_str = str(pat, 'ISO-8859-1')
        res_str = translate(pat_str)
        res = bytes(res_str, 'ISO-8859-1')
    else:
        res = translate(pat)
    return re.compile(res).match


def filter(names, pat):
    """Construct a list from those elements of the iterable NAMES that match PAT."""
    result = []
    pat = os.path.normcase(pat)
    match = _compile_pattern(pat)

    for name in names:
        if match(os.path.normcase(name)):
            result.append(name)
    return result


def translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    """

    STAR = object()
    res = []
    add = res.append
    i, n = 0, len(pat)
    while i < n:
        c = pat[i]
        i = i+1
        if c == '*':
            # compress consecutive `*` into one
            if (not res) or res[-1] is not STAR:
                add(STAR)
        elif c == '?':
            add('.')
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            if j >= n:
                add('\\[')
            else:
                stuff = pat[i:j]
                if '-' not in stuff:
                    stuff = stuff.replace('\\', r'\\')
                else:
                    chunks = []
                    k = i+2 if pat[i] == '!' else i+1
                    while True:
                        k = pat.find('-', k, j)
                        if k < 0:
                            break
                        chunks.append(pat[i:k])
                        i = k+1
                        k = k+3
                    chunk = pat[i:j]
                    if chunk:
                        chunks.append(chunk)
                    else:
                        chunks[-1] += '-'
                    # Remove empty ranges -- invalid in RE.
                    for k in range(len(chunks)-1, 0, -1):
                        if chunks[k-1][-1] > chunks[k][0]:
                            chunks[k-1] = chunks[k-1][:-1] + chunks[k][1:]
                            del chunks[k]
                    # Escape backslashes and hyphens for set difference (--).
                    # Hyphens that create ranges shouldn't be escaped.
                    stuff = '-'.join(s.replace('\\', r'\\').replace('-', r'\-')
                                     for s in chunks)
                # Escape set operations (&&, ~~ and ||).
                stuff = re.sub(r'([&~|])', r'\\\1', stuff)
                i = j+1
                if not stuff:
                    # Empty range: never match.
                    add('(?!)')
                elif stuff == '!':
                    # Negated empty range: match any character.
                    add('.')
                else:
                    if stuff[0] == '!':
                        stuff = '^' + stuff[1:]
                    elif stuff[0] in ('^', '['):
                        stuff = '\\' + stuff
                    add(f'[{stuff}]')
        else:
            add(re.escape(c))
    assert i == n

    # Deal with STARs.
    inp = res
    res = []
    add = res.append
    i, n = 0, len(inp)
    # Fixed pieces at the start?
    while i < n and inp[i] is not STAR:
        add(inp[i])
        i += 1
    # Now deal with STAR fixed STAR fixed ...
    # For an interior `STAR fixed` pairing, we want to do a minimal
    # .*? match followed by `fixed`, with no possibility of backtracking.
    # We can't spell that directly, but can trick it into working by matching
    #    .*?fixed
    # in a lookahead assertion, save the matched part in a group, then
    # consume that group via a backreference. If the overall match fails,
    # the lookahead assertion won't try alternatives. So the translation is:
    #     (?=(?P<name>.*?fixed))(?P=name)
    # Group names are created as needed: g0, g1, g2, ...
    # The numbers are obtained from _nextgroupnum() to ensure they're unique
    # across calls and across threads. This is because people rely on the
    # undocumented ability to join multiple translate() results together via
    # "|" to build large regexps matching "one of many" shell patterns.
    while i < n:
        assert inp[i] is STAR
        i += 1
        if i == n:
            add(".*")
            break
        assert inp[i] is not STAR
        fixed = []
        while i < n and inp[i] is not STAR:
            fixed.append(inp[i])
            i += 1
        fixed = "".join(fixed)
        if i == n:
            add(".*")
            add(fixed)
        else:
            groupnum = count + 1
            add(f"(?=(?P<g{groupnum}>.*?{fixed}))(?P=g{groupnum})")
    assert i == n
    res = "".join(res)
    return fr'(?s:{res})\Z'
