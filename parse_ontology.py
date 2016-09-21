from itertools import repeat
import re
from orangecontrib.bio.ontology import OBOOntology


def get_rex_value(regex, str):
    """
    Wrapper for regex parsing functions.

    Returns None if parsing fails.
    """
    try:
        return regex.search(str).group()
    except AttributeError:
        return None


def get_obo_id(str):
    """
    Get OBO id from column header.

    Throw exception if parsing fails.

    >>> get_obo_id("tpm of 293SLAM rinderpest infection, 00hr, biol_rep1.CNhs14406.13541-145H4")
    'FF:13541-145H4'
    """
    OBO_ID_REGEX = re.compile(r'CNhs\d+.(\w+)-(\w+)')
    return "FF:" + "-".join(OBO_ID_REGEX.search(str).groups())


def get_lib_id(str):
    """
    Get library id from column header

    Throw exception if parsing failes.

    >>> get_lib_id("tpm of 293SLAM rinderpest infection, 00hr, biol_rep1.CNhs14406.13541-145H4")
    'CNhs14406'
    """
    LIB_ID_REGEX = re.compile(r'CNhs(\d+)')
    return LIB_ID_REGEX.search(str).group()


def get_time(str):
    """
    Parse time from column header

    >>> get_time("tpm of 293SLAM rinderpestday01 infectionday01, 00hr, biol_rep1.CNhs14406.13541-145H4")
    'day01'
    >>> get_time("tpm of 293SLAM rinderpestdayd01 infectionddady01, 00hr, biol_rep1.CNhs14406.13541-145H4")
    '00hr'
    >>> get_time("tpm of 293SLAM rinderpestdayd01 infectionddady01, 15min biol_rep1.CNhs14406.13541-145H4")
    '15min'
    """
    TIME_REGEX = re.compile(r'(\d+)(hr|min)|day(\d+)')
    return get_rex_value(TIME_REGEX, str)


def get_donor(str):
    """
    Parse donor from column header.

    >>> get_donor("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, biol_rep1.CNhs14406.13541-145H4")
    'donor1'
    >>> get_donor("tpm of 293SLAM rinderpestdayd01 infection, 00hr, dondor1, biol_rep1.CNhs14406.13541-145H4")

    """
    DONOR_REGEX = re.compile(r'donor(\d+)')
    return get_rex_value(DONOR_REGEX, str)


def get_replicate(str):
    """
    Parse replicate from column header

    >>> get_replicate("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, biol_rep1.CNhs14406.13541-145H4")
    'biol_rep1'
    >>> get_replicate("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, rep1.CNhs14406.13541-145H4")
    'rep1'

    """
    REPLICATE_REGEX = re.compile(r'((biol|tech)_)?rep(\d+)')
    return get_rex_value(REPLICATE_REGEX, str)


def contains_term(term, tag_name, tag_value):
    """Check if a set of tags (from a certain term) contains a certain annotation (e.g. is_a: 24-hour-sample)"""
    return any(a == tag_name and b == tag_value for a, b in term.tags())

def compare_time(string, obo_id, obo):
    """
    Compare the time-string from the header and the corresponding ontology term.
    Return true if the two times are considered to be identical.

    Args:
        string: time string
        obo_id: ontology term id (e.g. FF:0000357)
        obo: OBOOntology object

    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> compare_time("00hr", "FF:0000357", obo)
    True
    >>> compare_time("24hr", "FF:0000357", obo)
    False
    """
    hour_terms = [term.id for term in obo.child_terms("UO:0000032")]
    minute_terms = [term.id for term in obo.child_terms("UO:0000031")]
    day_terms = [term.id for term in obo.child_terms("UO:0000033")]

    NO_REGEX = re.compile(r'(\d+)')
    if 'day' in string:
        if obo_id not in day_terms:
            return False
    elif 'hr' in string:
        if obo_id not in hour_terms:
            return False
    elif 'min' in string:
        if obo_id not in minute_terms:
            return False
    else:
        return False

    term_name = obo.term(obo_id).name
    if int(NO_REGEX.search(string).group()) == int(NO_REGEX.search(term_name).group()):
        return True
    else:
        return False


def compare_replicates(string, obo_id):
    """
    return true, if the replicate type is considered to be identical

    >>> compare_replicates("biol_rep1", "EFO:0002091")
    True
    >>> compare_replicates("tech_rep1", "EFO:0002091")
    False

    """
    tech_rep = "EFO:0002090"
    biol_rep = "EFO:0002091"

    if "tech_rep" in string and obo_id == tech_rep:
        return True
    elif "biol_rep" in string and obo_id == biol_rep:
        return True
    else:
        return False


if __name__ == "__main__":
    obo = OBOOntology()
    obo.load(open("data/ff-phase2-140729.obo.txt"))

    

