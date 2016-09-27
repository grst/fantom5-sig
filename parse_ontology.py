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
    >>> get_time("tpm of 293SLAM rinderpestd infectionday01, 00hr, biol_rep1.CNhs14406.13541-145H4")
    'day01;00hr'
    >>> get_time("tpm of 293SLAM rinderpestd infectionday12, biol_rep1.CNhs14406.13541-145H4")
    'day12'
    >>> get_time("tpm of 293SLAM rinderpestdayd01 infectionddady01, 00hxr, biol_rep1.CNhs14406.13541-145H4")

    >>> get_time("tpm of 293SLAM rinderpestd infectiond, 01hr40min, biol_rep1.CNhs14406.13541-145H4")
    '01hr40min'
    """
    time = {"hr": None, "min": None, "day": None}
    TIME_REGEX = re.compile(r'(\d+)(hr|min)|day(\d+)')
    INT_REGEX = re.compile(r'(\d+)')
    for match_obj in TIME_REGEX.finditer(str):
        time_str = match_obj.group()
        for unit in time:
            if unit in time_str:
                assert time[unit] is None, 'multiple times per unit {} not allowed: {}'.format(unit, str)
                time[unit] = INT_REGEX.search(time_str).group()

    return time_dict_to_str(time)


def time_dict_to_str(time_dict):
    """
    Format a dictionary `time = {"hr": j, "min": k, "day": l}` to a string e.g. 02hr40min.

    >>> time_dict_to_str({"hr": None, "min": None, "day": None})

    >>> time_dict_to_str({"hr": None, "min": None, "day": 1})
    'day01'
    >>> time_dict_to_str({"hr": 12, "min": None, "day": "01"})
    'day01;12hr'
    >>> time_dict_to_str({"hr": 12, "min": 15, "day": None})
    '12hr15min'
    """
    out = []
    if time_dict["day"] is not None:
        out.append("day{:02d}".format(int(time_dict["day"])))
        if time_dict["hr"] is not None or time_dict['min'] is not None:
            out.append(";")  # we need a separator in that case
    if time_dict['hr'] is not None:
        out.append("{:02d}hr".format(int(time_dict['hr'])))
    if time_dict['min'] is not None:
        out.append("{:02d}min".format(int(time_dict['min'])))
    out = "".join(out)
    if out == "":
        return None
    else:
        return out


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


def ontology_to_time(obo, obo_id):
    """
    Convert an ontology id to a readable time string.

    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> ontology_to_time(obo, "FF:0000357")
    '00hr'

    """
    hour_terms, minute_terms, day_terms = get_time_terms(obo)
    NO_REGEX = re.compile(r'(\d+)')
    term = obo.term(obo_id)
    number = NO_REGEX.search(term.name).group()
    time_dict = {"hr": None, "min": None, "day": None}
    if obo_id in hour_terms:
        time_dict['hr'] = number
    elif obo_id in minute_terms:
        time_dict['min'] = number
    elif obo_id in day_terms:
        time_dict['day'] = number
    return time_dict_to_str(time_dict)


def get_sample_type_from_ontology(obo, obo_term):
    """
    Get the sample_type from the ontology.

    There are three sample types defined in the ontology. The sample belongs to
    a certain type if it is a descendant of the respective type definition object.

    Args:
        obo: OBOOntology Object
        obo_term: OBOObject (term)

    Returns:
        None/primary cell/tissue/cell line

    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> obo_term = obo.term("FF:10100-102D1")  # tpm of uterus, adult, pool1.CNhs1167...
    >>> get_sample_type_from_ontology(obo, obo_term)
    'tissue'

    """
    mapping = {
        "FF:0000002": "primary cell",
        "FF:0000004": "tissue",
        "FF:0000003": "cell line",
    }
    super_terms = [term.id for term in obo.super_terms(obo_term.id)]
    sample_type = []  # cases like FF:11931-125I5 which are not unique
    for key, val in mapping.items():
        if key in super_terms:
            sample_type.append(val)
    return sample_type


def process_sample_name(sample_info):
    """
    Extract sample information from the sample name.

    >>> pprint(process_sample_name("tpm of 293SLAM rinderpest infection, 00hr, biol_rep1.CNhs14406.13541-145H4"))
    {'biol_rep': 'biol_rep1',
     'donor': None,
     'lib_id': 'CNhs14406',
     'name_orig': 'tpm of 293SLAM rinderpest infection, 00hr, '
                  'biol_rep1.CNhs14406.13541-145H4',
     'obo_id': 'FF:13541-145H4',
     'tech_rep': None,
     'time': '00hr'}

    """
    info_n = dict()
    info_n["obo_id"] = get_obo_id(sample_info)
    logging.info("{}: Parsing information from sample name".format(info_n["obo_id"]))

    info_n["lib_id"] = get_lib_id(sample_info)
    info_n["name_orig"] = sample_info

    # values parsed from name
    # we use the 'original' name here, as some information e.g. tech_rep is not available
    # in the name retrieved from the ontology.
    info_n["donor"] = get_donor(sample_info)  # donor is some sort of biological replicate
    info_n["time"] = get_time(sample_info)
    info_n["tech_rep"] = get_tech_replicate(sample_info)
    info_n["biol_rep"] = get_biol_replicate(sample_info)

    assert not (bool(info_n["biol_rep"]) and bool(info_n["donor"])), \
        "as donor is a form of biological replicate they should not co-occur in a name: {}".format(sample_info)

    return info_n


def process_sample_ontology(obo, sample_info):
    """
     loops through all is_a relationships in tags and look if it contains any relevant annotation.
     Here, we extract the time and whether the sample is a biological or technical replicate.

     Args:
         obo: OBOOntology Object
         obo_term: OBOObject (term)

     Returns:
         time_o: term_id of a TIME ontology or None if not specified.
         tech_rep_o: True, if the sample is a technical replicate, else None
         biol_rep_o, True, if the sample is a biological replicate, else None

    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> sample_info = "tpm of occipital lobe, fetal, donor1.CNhs11784.10073-102A1"
    >>> pprint(process_sample_ontology(obo, sample_info))
    {'biol_rep': True,
     'obo_id': 'FF:10073-102A1',
     'sample_type': 'tissue',
     'tech_rep': None,
     'time': None}
    """
    info_o = {
        "tech_rep": None,
        "biol_rep": None,
        "time": None,
        "obo_id": get_obo_id(sample_info),
        "lib_id": get_lib_id(sample_info),
    }
    logging.info("{}: Searching Ontology".format(info_o["lib_id"]))
    obo_term = obo.term(info_o["obo_id"])
    info_o["name"] = obo_term.name
    tags = obo_term.tags()
    for tag, tag_value, _, _ in tags:
        if tag == "is_a":
            if is_time_term(obo, tag_value):
                assert info_o["time"] is None, 'multiple matches: {0}'.format(tags)
                info_o["time"] = ontology_to_time(obo, tag_value)
            if tag_value == TECH_REP:
                assert info_o["tech_rep"] is None, 'multiple matches: {0}'.format(tags)
                info_o["tech_rep"] = True
            if tag_value == BIOL_REP:
                assert info_o["biol_rep"] is None, 'multiple matches: {0}'.format(tags)
                info_o["biol_rep"] = True
    info_o["sample_type"] = get_sample_type_from_ontology(obo, obo_term)
    return info_o


def merge_sample_info(info_n, info_o, info_si, annot_notes=[]):
    """
    Put the information from name, ontology and supplementary information together.
    Check for consistency and take note, if information is lacking in the ontology.

    Args:
        info_n: dict, info from name, retrieve through process_sample_name
        info_o: dict, info from ontology, retrieve trough process_sample_ontology
        info_si: dict, info from supplement, get from data frame
        annot_notes: list passed by reference that will be filled with a note if an annotation is
            missing in the ontology

    Returns:
        annot, dict with the merged annotations

    >>> obo = OBOOntology()
    >>> obo.load(open("data/ff-phase2-140729.obo"))
    >>> sample_info = "tpm of 293SLAM rinderpest infection, 00hr, biol_rep1.CNhs14406.13541-145H4"
    >>> info_n = process_sample_name(sample_info)
    >>> info_o = process_sample_ontology(obo, sample_info)
    >>> info_si = {"obo_id": "FF:13541-145H4", "sample_type": "tissue"}
    >>> annotation_notes = []
    >>> pprint(merge_sample_info(info_n, info_o, info_si, annotation_notes))
    {'biol_rep': True,
     'donor': None,
     'lib_id': 'CNhs14406',
     'name': None,
     'name_orig': 'tpm of 293SLAM rinderpest infection, 00hr, '
                  'biol_rep1.CNhs14406.13541-145H4',
     'obo_id': 'FF:13541-145H4',
     'sample_type': 'tissue',
     'tech_rep': False,
     'time': '00hr'}
    >>> pprint(annotation_notes)
    [{'field_name': 'biol_rep',
      'lib_id': 'CNhs14406',
      'new_value': 'biol_rep1',
      'obo_id': 'FF:13541-145H4'}]

    apparently, for CNhs14406, the ontology contains no information, that is is a biological replicate.

    """
    assert info_n["obo_id"] == info_o["obo_id"] == info_si["obo_id"] is not None, "obo_ids not matching"
    assert info_n["lib_id"] == info_o["lib_id"] == info_si["lib_id"] is not None, "lib_ids not matching"
    logging.info("{}: Merging Information".format(info_n["lib_id"]))

    def add_annotation_note(field_name, new_value):
        """add note, that an annotation is missing in the ontology"""
        logging.debug("{}: missing in ontology. ".format(field_name))
        annot_notes.append({
            "lib_id": info_n["lib_id"],
            "obo_id": info_n["obo_id"],
            "field_name": field_name,
            "new_value": new_value
        })

    def simply_merge(field_name):
        """Merge the three dicts, assert that the same if not None or key does not exist"""
        dicts = [info_n, info_o, info_si]
        vals = [d.get(field_name, None) for d in dicts]
        true_vals = [v for v in vals if v is not None]
        assert len(set(true_vals)) <= 1, "value mismatch"
        val = true_vals[0] if len(true_vals) > 0 else None
        if vals[1] is None and len(true_vals) > 1:
            add_annotation_note(field_name, val)
        return val

    def merge_biol_rep():
        if bool(info_n["biol_rep"]) or bool(info_n["donor"]):
            if not bool(info_o["biol_rep"]):
                add_annotation_note("biol_rep", info_n["biol_rep"] if info_n["biol_rep"] else info_n["donor"])
        return bool(info_o["biol_rep"]) or bool(info_n["biol_rep"]) or bool(info_n["donor"])

    def merge_tech_rep():
        if bool(info_n["tech_rep"]):
            if not bool(info_o["tech_rep"]):
                add_annotation_note("tech_rep", info_n["tech_rep"])
        return bool(info_o["tech_rep"]) or bool(info_n["tech_rep"])

    def merge_sample_type():
        # here, we tolerate inconsistencies and prefer the ontology if available
        if len(info_o["sample_type"]) > 0:
            if info_si["sample_type"] is not None and (info_si["sample_type"] not in info_o["sample_type"]):
                logging.warning("sample_type: inconsistent. Ontology: {}, SI: {}".format(
                    info_o["sample_type"], info_si["sample_type"]))
            if len(info_o["sample_type"]) == 1:  # there are cases with multiple sample types in the ontology
                return info_o["sample_type"][0]
            else:
                logging.warning("sample_type: multiple sample types in ontology: {}".format(info_o["sample_type"]))
                return "multiple"
        else:
            add_annotation_note("sample_type", info_si["sample_type"])
            return info_si["sample_type"]

    annot = {
        "lib_id": info_n["lib_id"], # no merge required due to assertion
        "obo_id": info_n["obo_id"], # no merge required due to assertion
        "biol_rep": merge_biol_rep(),
        "tech_rep": merge_tech_rep(),
        "donor": simply_merge("donor"),
        "time": simply_merge("time"),
        "name": simply_merge("name"),
        "name_orig": simply_merge("name_orig"),
        "sample_type": merge_sample_type()
    }

    return annot

