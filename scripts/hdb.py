"""Which BTO blocks HDB itself lists as completed.

Source: HDB Property Information on data.gov.sg (official, updated by HDB), which
lists every HDB block with the year it was completed. A BTO block only appears
there once it is built, so we match each project's block numbers + street.

Writes nothing itself; update.py stores the result in data.json["hdb"] as
{project label: [blocks completed, blocks in project, latest completion year]}.
"""
import json, re, urllib.request

RES = "d_17f5382f26140b1fdae0ba2ef6239d2f"
API = "https://data.gov.sg/api/action/datastore_search?resource_id={r}&limit=5000&offset={o}"
SRC = "https://data.gov.sg/datasets/d_17f5382f26140b1fdae0ba2ef6239d2f/view"

AB = {"AVENUE": "AVE", "GARDEN": "GDN", "GARDENS": "GDNS", "STREET": "ST", "ROAD": "RD", "DRIVE": "DR",
      "CENTRAL": "CTRL", "CRESCENT": "CRES", "NORTH": "NTH", "SOUTH": "STH", "PLACE": "PL", "CLOSE": "CL",
      "TERRACE": "TER", "HEIGHTS": "HTS", "PARK": "PK", "UPPER": "UPP", "BUKIT": "BT", "JALAN": "JLN",
      "LORONG": "LOR", "TANJONG": "TG", "KAMPONG": "KG", "COMMONWEALTH": "C'WEALTH", "SAINT": "ST",
      "MOUNT": "MT", "SQUARE": "SQ", "CENTRE": "CTR", "BOULEVARD": "BLVD", "INDUSTRIAL": "IND",
      "GREEN": "GRN", "MARKET": "MKT"}


def _norm(street):
    return [AB.get(w, w) for w in street.upper().replace("'", "").replace("’", "").split()]


def _same_street(a, b):
    a, b = _norm(a), _norm(b)
    return a == b or (a[:1] == b[:1] and a[-1:] == b[-1:])


def fetch(get_json):
    rows, off = [], 0
    while off < 50000:
        r = get_json(API.format(r=RES, o=off))
        recs = ((r or {}).get("result") or {}).get("records") or []
        rows += recs
        if len(recs) < 5000:
            break
        off += 5000
    return rows


def completed(bto_rows, hdb_rows):
    """bto_rows use the data.json layout: [label, type, launch, est, delayed, remark, roads, blks, postals, ll]."""
    by_blk = {}
    for h in hdb_rows:
        by_blk.setdefault(h["blk_no"].upper(), []).append(h)
    out = {}
    for r in bto_rows:
        label, launch, roads, blks = r[0], r[2], [x for x in (r[6] or "").split("|") if x], (r[7] or "").split()
        if not (launch and blks and roads):
            continue
        min_year = int(launch[:4]) + 3  # no BTO is built in under ~3 years; older same-numbered blocks are ignored
        done, nonres, years = 0, 0, []
        for b in blks:
            hit = next((h for h in by_blk.get(b.upper(), [])
                        if h["year_completed"].isdigit() and int(h["year_completed"]) >= min_year
                        and any(_same_street(rd, h["street"]) for rd in roads)), None)
            if not hit:
                continue
            if hit.get("residential") == "Y":
                done += 1
                years.append(int(hit["year_completed"]))
            else:
                nonres += 1  # car park etc.; doesn't count towards homes
        if done:
            out[label] = [done, len(blks) - nonres, max(years)]
    return out


if __name__ == "__main__":
    import os
    UA = {"User-Agent": "Mozilla/5.0"}
    gj = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
    d = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data.json")))
    res = completed(d["bto"], fetch(gj))
    for k, v in sorted(res.items(), key=lambda kv: -kv[1][0] / kv[1][1]):
        print(f"{v[0]}/{v[1]} blocks, {v[2]}  {k}")
