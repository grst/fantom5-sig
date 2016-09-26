import re
from orangecontrib.bio.ontology import OBOOntology
import itertools
import logging
from pprint import pprint

# The IDs from the ontology file
TECH_REP = "EFO:0002090"
BIOL_REP = "EFO:0002091"
HOUR_TERM = "UO:0000032"
MINUTE_TERM = "UO:0000031"
DAY_TERM = "UO:0000033"


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
    Traceback (most recent call last):
    ...
    AssertionError: multiple times per unit day not allowed: tpm of 293SLAM rinderpestday01 infectionday01, 00hr, biol_rep1.CNhs14406.13541-145H4
    >>> pprint(get_time("tpm of 293SLAM rinderpestd infectionday01, 00hr, biol_rep1.CNhs14406.13541-145H4"))
    {'day': 'day01', 'hr': '00hr', 'min': None}
    >>> pprint(get_time("tpm of 293SLAM rinderpestdayd01 infectionddady01, 00hxr, biol_rep1.CNhs14406.13541-145H4"))
    {'day': None, 'hr': None, 'min': None}
    >>> pprint(get_time("tpm of 293SLAM rinderpestd infectiond, 01hr40min, biol_rep1.CNhs14406.13541-145H4"))
    {'day': None, 'hr': '01hr', 'min': '40min'}
    """
    time = {"hr": None, "min": None, "day": None}
    TIME_REGEX = re.compile(r'(\d+)(hr|min)|day(\d+)')
    for match_obj in TIME_REGEX.finditer(str):
        time_str = match_obj.group()
        for unit in time:
            if unit in time_str:
                assert time[unit] is None, 'multiple times per unit {} not allowed: {}'.format(unit, str)
                time[unit] = time_str

    return time


def get_donor(str):
    """
    Parse donor from column header.

    >>> get_donor("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, biol_rep1.CNhs14406.13541-145H4")
    'donor1'
    >>> get_donor("tpm of 293SLAM rinderpestdayd01 infection, 00hr, dondor1, biol_rep1.CNhs14406.13541-145H4")

    """
    DONOR_REGEX = re.compile(r'donor(\d+)')
    return get_rex_value(DONOR_REGEX, str)


def get_biol_replicate(str):
    """
    Parse biological replicate from column header.
    Both rep1 and biol_rep1 are considered as a biological replicate.

    >>> get_biol_replicate("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, biol_rep1.CNhs14406.13541-145H4")
    'biol_rep1'
    >>> get_biol_replicate("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, rep1.CNhs14406.13541-145H4")
    'rep1'
    >>> get_biol_replicate("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, CNhs14406.13541-145H4")

    >>> get_biol_replicate("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, some_rep1.CNhs14406.13541-145H4")

    """
    REPLICATE_REGEX = re.compile(r'([ ]+|biol_)rep(\d+)')
    rep = get_rex_value(REPLICATE_REGEX, str)
    if rep is not None:
        rep = rep.strip()
    return rep


def get_tech_replicate(str):
    """
    Parse replicate from column header

    >>> get_tech_replicate("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, tech_rep1.CNhs14406.13541-145H4")
    'tech_rep1'
    >>> get_tech_replicate("tpm of 293SLAM rinderpestdayd01 infection, 00hr, donor1, rep1.CNhs14406.13541-145H4")

    """
    REPLICATE_REGEX = re.compile(r'tech_rep(\d+)')
    return get_rex_value(REPLICATE_REGEX, str)


def contains_term(term, tag_name, tag_value):
    """Check if a set of tags (from a certain term) contains a certain annotation (e.g. is_a: 24-hour-sample)"""
    return any(a == tag_name and b == tag_value for a, b in term.tags())


def get_time_terms(obo):
    hour_terms = [term.id for term in obo.child_terms(HOUR_TERM)]
    minute_terms = [term.id for term in obo.child_terms(MINUTE_TERM)]
    day_terms = [term.id for term in obo.child_terms(DAY_TERM)]
    return hour_terms, minute_terms, day_terms


def is_time_term(obo, term_id):
    """
    Return true if the term_id is a time-ontology

    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> is_time_term(obo, "FF:0000357")
    True
    >>> is_time_term(obo, "FF:0350357")
    False
    """
    return True if term_id in itertools.chain(*get_time_terms(obo)) else False


def compare_time(obo, string, obo_id):
    """
    Compare the time-string from the header and the corresponding ontology term.
    Return true if the two times are considered to be identical.

    Args:
        string: time string
        obo_id: ontology term id (e.g. FF:0000357)
        obo: OBOOntology object

    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> compare_time(obo, "00hr", "FF:0000357")
    True
    >>> compare_time(obo, "24hr", "FF:0000357")
    False
    """
    hour_terms, minute_terms, day_terms = get_time_terms(obo)

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


def ontology_to_time(obo, obo_id):
    """
    Convert an ontology id to a readable time string.

    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> ontology_to_time(obo, "FF:0000357")
    '0hr'

    """
    hour_terms, minute_terms, day_terms = get_time_terms(obo)
    NO_REGEX = re.compile(r'(\d+)')
    term = obo.term(obo_id)
    number = NO_REGEX.search(term.name).group()
    if obo_id in hour_terms:
        return "{0}hr".format(number)
    elif obo_id in minute_terms:
        return "{0}min".format(number)
    elif obo_id in day_terms:
        return "day{0}".format(number)
    else:
        return None


def get_annotation_from_ontology(obo, tags):
    """
    loops through all is_a relationships in tags and look if it contains any relevant annotation.
    Here, we extract the time and whether the sample is a biological or technical replicate.

    Args:
        obo: OBOOntology Object
        tags: tags of an obo term

    Returns:
        time_o: term_id of a TIME ontology or None if not specified.
        tech_rep_o: True, if the sample is a technical replicate, else None
        biol_rep_o, True, if the sample is a biological replicate, else None

    """
    tech_rep_o = None
    biol_rep_o = None
    time_o = None
    for tag, tag_value, _, _ in tags:
        if tag == "is_a":
            if is_time_term(obo, tag_value):
                assert time_o is None, 'multiple matches: {0}'.format(tags)
                time_o = tag_value
            if tag_value == TECH_REP:
                assert tech_rep_o is None, 'multiple matches: {0}'.format(tags)
                tech_rep_o = True
            if tag_value == BIOL_REP:
                assert biol_rep_o is None, 'multiple matches: {0}'.format(tags)
                biol_rep_o = True
    return time_o, tech_rep_o, biol_rep_o


def process_time(obo, time_n, time_o, annot_notes = lambda x: None):
    """
    Compares the time extracted from the sample name and from the ontology.

    Asserts that both times are equal, if available.
    Ontology term-ids are converted to a readable time output (e.g. 12hr instead of FF:0000374)

    Args:
        obo: OBOOntology Object
        time_n: time extracted from the sample name (something like 12hr) with get_time, i.e.
                a dictionary {'day': ..., 'hr': ..., 'min': ...}
        time_o: time extracted from the sample ontology (term-id)

    Returns:
        time_string (e.g. 12hr) or None of no time found.

    """
    if any(time_n.values()) and time_o:
        assert sum(x is not None for x in time_n.values()) == 1, 'multiple time units in name string, but only one in ' \
                                                                 'ontology'
        time_n_val = next(x for x in time_n.values() if x is not None)  # get the one element that is not None
        assert compare_time(obo, time_n_val, time_o), "mismatching times: {0}, {1}".format(time_n, time_o)
        logging.debug("consistent time information between term name and ontoloty.")
        return time_n_val
    elif time_o:
        logging.debug("using time information from ontology only.")
        return ontology_to_time(obo, time_o)
    elif any(time_n.values()):
        logging.debug("using time information from term name only.")
        # we have to handle cases such as 01hr40min
        out = []
        if time_n["day"] is not None:
            out.append(time_n["day"])
            if time_n["hr"] is not None or time_n['min'] is not None:
                out.append(";")  # we need a separator in that case
        if time_n['hr'] is not None:
            out.append(time_n['hr'])
        if time_n['min'] is not None:
            out.append(time_n['min'])

        time_out = "".join(out)
        # create a note in annot_notes for the sake of fixing the ontology later
        annot_notes(time_out)
        return time_out
    else:
        logging.debug("no time information available.")
        return None


def add_annotation_note(annot_notes, lib_id, obo_id, field_name, new_value):
    """
    add note, that an annotation is missing in the ontology

    Args:
        annot_notes: list, to which the note will be appended
        lib_id: CNhs?????
        obo_id: FF:?????-?????
        field_name: either "biol_rep", "tech_rep", or "time"
        new_value: the value that was extracted from the name and is missing in the ontology.

    """
    assert field_name in ["biol_rep", "tech_rep", "time"]
    logging.debug("{} missing in ontology. ".format(field_name))
    annot_notes.append({"lib_id": lib_id, "obo_id": obo_id, "field_name": field_name, "new_value": new_value})


def process_sample_description(obo, sample_info, annot_notes=[]):
    """
    Get sample annotation from ontology and from the sample name.
    Check for consistency between name and Ontology and merge the
    two sources in case the data is only available in one.

    Args:
        obo: OBOOntology Object
        sample_info: one line from the extracted column_vars, e.g.
            "tpm of 293SLAM rinderpest infection, 00hr, biol_rep1.CNhs14406.13541-145H4"
        annot_notes: list passed by reference that will be filled with a note if an annotation is
            missing in the ontology.

    Returns:
        annot: dictionary with column annotations


    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> annotation_notes = []
    >>> pprint(process_sample_description(obo, \
            "tpm of 293SLAM rinderpest infection, 00hr, biol_rep1.CNhs14406.13541-145H4", \
            annotation_notes))
    {'biol_rep': True,
     'donor': None,
     'lib_id': 'CNhs14406',
     'name': '293SLAM rinderpest infection, 00hr, biol_rep1',
     'name_orig': 'tpm of 293SLAM rinderpest infection, 00hr, '
                  'biol_rep1.CNhs14406.13541-145H4',
     'obo_id': 'FF:13541-145H4',
     'tech_rep': False,
     'time': '00hr'}
    >>> pprint(annotation_notes)
    [{'field_name': 'biol_rep',
      'lib_id': 'CNhs14406',
      'new_value': 'biol_rep1',
      'obo_id': 'FF:13541-145H4'}]
    apparently, for CNhs14406, the ontology contains no information, that is is a biological replicate.

    """

    def add_time_annotation_note(time_value):
        """same as add_annotation_note, only specific for the time annotation"""
        add_annotation_note(annot_notes, lib_id, obo_id, "time", time_value)

    logging.info("Processing sample '{}'".format(sample_info))
    obo_id = get_obo_id(sample_info)
    lib_id = get_lib_id(sample_info)
    obo_term = obo.term(obo_id)
    tags = obo_term.tags()
    name_orig = sample_info
    name = obo_term.name

    # values parsed from name
    # we use the 'original' name here, as some information e.g. tech_rep is not available
    # in the name retrieved from the ontology.
    donor_n = get_donor(sample_info)  # donor is some sort of biological replicate
    time_n = get_time(sample_info)
    tech_rep_n = get_tech_replicate(sample_info)
    biol_rep_n = get_biol_replicate(sample_info)

    assert not (bool(biol_rep_n) and bool(donor_n)), "as donor is a form of biological replicate they should" \
                                                     "not co-occur in a name: {}".format(sample_info)

    # values parsed from ontology
    time_o, tech_rep_o, biol_rep_o = get_annotation_from_ontology(obo, tags)

    # verbose logging
    if bool(biol_rep_o) and (bool(biol_rep_n) or bool(donor_n)):
        logging.debug("consistent annotation of biological replicate. ")
    if bool(tech_rep_o) and bool(tech_rep_n):
        logging.debug("consistent annotation of technical replicate. ")

    # values are missing in ontology
    if (bool(biol_rep_n) or bool(donor_n)) and not bool(biol_rep_o):
        add_annotation_note(annot_notes, lib_id, obo_id, "biol_rep", biol_rep_n if bool(biol_rep_n) else donor_n)
    if bool(tech_rep_n) and not bool(tech_rep_o):
        add_annotation_note(annot_notes, lib_id, obo_id, "tech_rep", tech_rep_n)

    # logging and missing values for time are handled here:
    time = process_time(obo, time_n, time_o, add_time_annotation_note)

    # make annotation dict
    annot = {
        "lib_id": lib_id,
        "name": name,
        "name_orig": name_orig,
        "obo_id": obo_id,
        "donor": donor_n,
        "time": time,
        "biol_rep": (bool(biol_rep_o) or bool(biol_rep_n) or bool(donor_n)),
        "tech_rep": (bool(tech_rep_o) or bool(tech_rep_n))
    }

    return annot
