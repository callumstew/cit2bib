#!/usr/bin/env python3
import requests
import sys
import re
import logging
import shelve
import os

cache = shelve.open(os.path.join(os.getenv("HOME"), '.cit2bib.cache'))

doi_pattern = re.compile('^(doi:)?(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?![%"#? ])\\S)+[a-zA-Z0-9])$')
arxiv_pattern = re.compile('(arXiv:)?(\d+\.\d+)(v\d)?')
pmid_pattern = re.compile('^(PMID:)?(\d{6,})$')
bibid_pattern = re.compile('(@[a-z]+{)([^,]+)')
cite_pattern = re.compile(r'\\cite\{([^}]+)\}')

logging.basicConfig()
logger = logging.getLogger('log')

def cache_wrapper(func):
    def from_cache(citation):
        if citation in cache:
            return cache[citation]
        else:
            ref = func(citation)
            if ref is not None:
                cache[citation] = ref
            return ref
    return from_cache

@cache_wrapper
def citation_type_func(citation):
    if doi_pattern.match(citation):
        logger.info(f'DOI detected: {citation}')
        doi = doi_pattern.match(citation).groups()[1]
        return doi2bib(doi)
    elif arxiv_pattern.match(citation):
        logger.info(f'ARXIV detected: {citation}')
        arxiv_id = arxiv_pattern.match(citation).groups()[1]
        return doi2bib(f'10.48550/arxiv.{arxiv_id}')
    elif pmid_pattern.match(citation):
        logger.info(f'PMID detected: {citation}')
        pmid = pmid_pattern.match(citation).groups()[1]
        doi = pm2doi(pmid)
        if doi:
            return doi2bib(doi)
    logger.info(f'No bibliography entry found for {citation}')


def doi2bib(doi: str):
    r = requests.get(f'https://doi.org/{doi}',
        headers={'Accept': 'application/x-bibtex; charset=utf-8'})
    if r.ok:
        return r.text


def pm2doi(pmid: str):
    r = requests.get(f'http://www.pubmedcentral.nih.gov/utils/idconv/v1.0/?format=json&ids={pmid}')
    print(r.json())
    if r.ok:
        try:
            return r.json()['records'][0]['doi']
        except:
            return None


def replace_id(bib, id):
    return bibid_pattern.sub(fr'\g<1>{id}', bib)


def parse_latex_log(log_fh):
    line = args.infile.readline()
    reference_ids = []
    while line:
        if line == "Package biblatex Warning: The following entry could not be found\n":
            args.infile.readline()
            rid = args.infile.readline().split()[1]
            reference_ids.append(rid)
        line = args.infile.readline()
    return reference_ids


def parse_tex(tex_fh):
    text = tex_fh.read()
    return cite_pattern.findall(text)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('--texfile', action=argparse.BooleanOptionalAction)
    parser.add_argument('--latex_log', action=argparse.BooleanOptionalAction)
    parser.add_argument('--debug', action=argparse.BooleanOptionalAction)
    parser.add_argument('--clear_cache', action=argparse.BooleanOptionalAction)
    args = parser.parse_args() 
    logger = logging.getLogger('log')
    if args.debug:
        logger.setLevel(logging.INFO)
    if args.texfile:
        reference_ids = parse_tex(args.infile)
    elif args.latex_log:
        reference_ids = parse_latex_log(args.infile)
    else:
        reference_ids = args.infile.read().split()
    for rid in reference_ids:
        logger.info(f'Reference ID: {rid}')
        if args.clear_cache:
            if rid in cache:
                del cache[rid]
        bib_str = citation_type_func(rid)
        if bib_str:
            bib_str = replace_id(bib_str, rid)
            bib_str = bib_str.replace('%2F', '/')
            args.outfile.write(bib_str.rstrip() + '\n')

cache.close()
