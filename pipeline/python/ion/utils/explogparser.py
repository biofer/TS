#!/usr/bin/python
# Copyright (C) 2012 Ion Torrent Systems, Inc. All Rights Reserved

__version__ = filter(str.isdigit, "$Revision: 17459 $")

import os
import sys
import datetime
import traceback
import json
import re
import string
import time
import ion.utils.logregexp as lre

PGM_START_TIME_FORMAT = "%a %b %d %H:%M:%S %Y"
PROTON_START_TIME_FORMAT = "%m/%d/%Y %H:%M:%S"
DB_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def extract_rig(folder):
    """Given the name of a folder storing experiment data, return the name
    of the PGM from which the date came."""
    return os.path.basename(os.path.dirname(folder))


def getparameter(parameterfile=None):

    #####################################################################
    # Load the analysis parameters and metadata from a json file passed in on the
    # command line with --params=<json file name>
    # we expect this loop to iterate only once. This is more elegant than
    # trying to index into ARGUMENTS.
    #####################################################################
    EXTERNAL_PARAMS = {}
    warnings = ''
    env = {}
    if parameterfile:
        env["params_file"] = parameterfile
    else:
        env["params_file"] = 'ion_params_00.json'
    afile = open(env["params_file"], 'r')
    EXTERNAL_PARAMS = json.loads(afile.read())
    afile.close()
    for k, v in EXTERNAL_PARAMS.iteritems():
        if isinstance(v, unicode):
            EXTERNAL_PARAMS[k] = str(v.encode('utf-8'))

    # Where the raw data lives (generally some path on the network)
    pathprefix = str(EXTERNAL_PARAMS['pathToData'])
    env['prefix'] = pathprefix

    #get the experiment json data
    env['exp_json'] = EXTERNAL_PARAMS.get('exp_json')

    env['platform'] = EXTERNAL_PARAMS.get('platform','Unspecified')
    env['instrumentName'] = EXTERNAL_PARAMS.get('pgmName','unknownInstrument')

    #this will get the exp data from the database
    exp_json = json.loads(env['exp_json'])
    if not isinstance(exp_json['log'], dict):
        exp_log_json = json.loads(exp_json['log'])
    else:
        exp_log_json = exp_json['log']

    env['flows'] = EXTERNAL_PARAMS.get('flows')
    env['notes'] = exp_json['notes']
    env['start_time'] = exp_log_json['start_time']

    env['blockArgs'] = EXTERNAL_PARAMS.get('blockArgs')

    #is it a thumbnail
    env['doThumbnail'] = EXTERNAL_PARAMS.get("doThumbnail")
    # get command line args
    env['beadfindArgs'] = EXTERNAL_PARAMS.get("beadfindArgs","")
    env['analysisArgs'] = EXTERNAL_PARAMS.get("analysisArgs","")
    env['basecallerArgs'] = EXTERNAL_PARAMS.get("basecallerArgs","")
    env['prebasecallerArgs'] = EXTERNAL_PARAMS.get("prebasecallerArgs","")
    env['recalibArgs'] = EXTERNAL_PARAMS.get("recalibArgs","")
    env['doBaseRecal'] = EXTERNAL_PARAMS.get("doBaseRecal", False)

    #previousReports
    env['previousReport'] = EXTERNAL_PARAMS.get("previousReport","")

    env['library'] = EXTERNAL_PARAMS.get("library","unknownLibrary")

    # this is the library reference name for the run taken from the library reference field in the database
    # old libraryName key check is needed for backwards compatibility for plugins
    env["referenceName"] = EXTERNAL_PARAMS.get("referenceName", "")  if 'referenceName' in EXTERNAL_PARAMS else EXTERNAL_PARAMS.get('libraryName')
    if not env["referenceName"]:
        env["referenceName"] = "none"
        warnings += "WARNING: referenceName redefine required.  set to none\n"

    dtnow = datetime.datetime.now()
    # the time at which the analysis was started, mostly for debugging purposes
    env["report_start_time"] = dtnow.strftime("%c")
    # name of current analysis
    env['resultsName'] = EXTERNAL_PARAMS.get("resultsName")
    # name of current experiment
    env['expName'] = EXTERNAL_PARAMS.get("expName")
    # user-input part of experiment name: R_2012_04_30_15_22_02_user_FOZ-389--R145025-CC409_allt_12878-asr
    # would get FOZ-389--R145025-CC409_allt_12878-asr
    env['shortRunName'] = env['expName'].split('_', 8)[-1]
    #library key input
    env['libraryKey'] = EXTERNAL_PARAMS.get("libraryKey","")
    if not env['libraryKey']:
        env['libraryKey'] = "TCAG"
        warnings += "WARNING: libraryKey redefine required.  set to TCAG\n"
    #path to the raw data
    env['pathToRaw'] = EXTERNAL_PARAMS.get("pathToData")
    #plugins
    env['plugins'] = EXTERNAL_PARAMS.get("plugins")
    #plan
    env['plan'] = EXTERNAL_PARAMS.get('plan', {})
    #eas
    env['experimentAnalysisSettings'] = EXTERNAL_PARAMS.get('experimentAnalysisSettings', {})
    # skipChecksum?
    env['skipchecksum'] = EXTERNAL_PARAMS.get('skipchecksum', False)
    # Do Full Align?
    env['align_full'] = EXTERNAL_PARAMS.get('align_full')

    env['flowOrder'] = EXTERNAL_PARAMS.get('flowOrder', "0").strip()
    # If flow order is missing, assume classic flow order:
    if env['flowOrder'] == "0":
        env['flowOrder'] = "TACG"
        warnings += "WARNING: floworder redefine required.  set to TACG\n"

    env['oninstranalysis'] = False
    try:
        if exp_log_json['oninstranalysis'] == "yes":
            env['oninstranalysis'] = True
    except:
        pass

    env['project'] = EXTERNAL_PARAMS.get('project')
    env['sample'] = EXTERNAL_PARAMS.get('sample')
    env['chipType'] = EXTERNAL_PARAMS.get('chiptype')
    env['barcodeId'] = EXTERNAL_PARAMS.get('barcodeId','')
    env['barcodeInfo'] = EXTERNAL_PARAMS.get('barcodeInfo')

    env['reverse_primer_dict'] = EXTERNAL_PARAMS.get('reverse_primer_dict')
    env['rawdatastyle'] = EXTERNAL_PARAMS.get('rawdatastyle', 'single')

    #extra JSON
    env['extra'] = EXTERNAL_PARAMS.get('extra', '{}')
    # Aligner options
    env['aligner_opts_extra'] = EXTERNAL_PARAMS.get('aligner_opts_extra', '{}')
    env['mark_duplicates'] = EXTERNAL_PARAMS.get('mark_duplicates')
    env['realign'] = EXTERNAL_PARAMS.get('realign')

    #get the name of the site
    env['site_name'] = EXTERNAL_PARAMS.get('site_name')

    env['runID'] = EXTERNAL_PARAMS.get('runid', 'ABCDE')


    env['tfKey'] = EXTERNAL_PARAMS.get('tfKey', '')
    if not env['tfKey']:
        env['tfKey'] = "ATCG"
        warnings += "WARNING: tfKey redefine required.  set to ATCG\n"

    env['SIGPROC_RESULTS'] = "sigproc_results"
    env['BASECALLER_RESULTS'] = "basecaller_results"
    env['ALIGNMENT_RESULTS'] = "./"

    # Sub directory to contain files for barcode enabled runs
    env['sam_parsed'] = EXTERNAL_PARAMS.get('sam_parsed')

    env['tmap_version'] = EXTERNAL_PARAMS.get('tmap_version')
    env['url_path'] = EXTERNAL_PARAMS.get('url_path')
    env['net_location'] = EXTERNAL_PARAMS.get('net_location')
    # net_location is set on masternode (in views.py) with "http://" + str(socket.getfqdn())
    env['master_node'] = env['net_location'].replace('http://', '')

    # figure out report type
    if env['rawdatastyle'] == 'single':
        env['report_type'] = 'wholechip'
    else:
        if "thumbnail" in env['pathToRaw']:
            env['report_type'] = 'thumbnail'
        else:
            env['report_type'] = 'composite'

    env['username'] = EXTERNAL_PARAMS.get('username')
    env['sampleInfo'] = EXTERNAL_PARAMS.get('sampleInfo', {})

    return env, warnings

def getparameter_minimal(parameterfile=None):

    EXTERNAL_PARAMS = {}
    if not parameterfile:
        parameterfile = 'ion_params_00.json'
    afile = open(parameterfile, 'r')
    EXTERNAL_PARAMS = json.loads(afile.read())
    afile.close()
    for k, v in EXTERNAL_PARAMS.iteritems():
        if isinstance(v, unicode):
            EXTERNAL_PARAMS[k] = str(v)

    env = EXTERNAL_PARAMS
    env['SIGPROC_RESULTS'] = "sigproc_results"
    env['BASECALLER_RESULTS'] = "basecaller_results"
    env['ALIGNMENT_RESULTS'] = "./"
    env['pathToRaw'] = ""

    env['libraryKey'] = EXTERNAL_PARAMS.get('libraryKey', "TCAG")
    env['tfKey'] = EXTERNAL_PARAMS.get('tfKey', "ATCG")

    env['report_type'] = ""

    return env


def load_log_path(filepath):
    (head, tail) = os.path.split(filepath)
    return load_log(head, tail)

def load_log(folder, logName):
    """Retrieve the contents of the experiment log found in ``folder``,
    or return ``None`` if no log can be found."""
    fname = os.path.join(folder, logName)
    if os.path.isfile(fname):
        infile = None
        try:
            infile = open(fname)
            text = infile.read()
        except IOError:
            text = None
        finally:
            if infile is not None:
                infile.close()
            if len(text) == 0:
                text = None
    else:
        text = None
    return text

ENTRY_MAP = {
    "gain": lre.float_parse,
    "datacollect_version": lre.int_parse,
    "liveview_version": lre.int_parse,
    "firmware_version": lre.int_parse,
    "fpga_version": lre.int_parse,
    "driver_version": lre.int_parse,
    "script_version": lre.dot_separated_parse,
    "board_version": lre.int_parse,
    "kernel_build": lre.kernel_parse,
    "prerun": lre.yn_parse,
    # TODO: Enumerate things that will break if this is changed
    # It is used to parse job files produced by the PGM, yes?
    "cycles": lre.int_parse,
    "livechip": lre.yn_parse,
    "continuous_clocking": lre.yn_parse,
    "auto_cal": lre.yn_parse,
    "frequency": lre.int_parse,
    "oversample": lre.oversample_parse,
    "frame_time": lre.float_parse,
    "num_frames": lre.int_parse,
    "autoanalyze": lre.yn_parse,
    "dac": lre.dac_parse,
    "cal_chip_hist": lre.space_separated_parse,
    "cal_chip_high_low_inrange": lre.cal_range_parse,
    "prebeadfind": lre.yn_parse,
    "flows": lre.int_parse,
    "analyzeearly": lre.yn_parse,
#    "chiptype": lre.chip_parse,
}

def parse_log(text):
    """Take the raw text of the experiment log, and return a dictionary
    of the entries contained in the log, parsed into the appropriate
    datatype.
    """

    ENTRY_RE = re.compile(r'^(?P<name>[^:]+)[:](?P<value>.*)$')
    CLEAN_RE = re.compile(r'\s|[/]+')

    def filter_non_printable(str_in):
        if isinstance(str_in, basestring):
            return ''.join([c for c in str_in if ord(c) > 31 or ord(c) == 9])
        else:
            return str_in

    def clean_name(name):
        no_ws = CLEAN_RE.sub("_", name)
        return no_ws.lower()

    def extract_entries(text):
        ret = []
        for line in text.split('\n'):
            match = ENTRY_RE.match(line)
            if match is not None:
                d = match.groupdict()
                ret.append((clean_name(d['name']), d['value'].strip()))
        return ret

    ret = {}
    entries = extract_entries(text)
    for name, value in entries:
        # utf-8 replace code to ensure we don't crash on invalid characters
        #ret[name] = ENTRY_MAP.get(name, lre.text_parse)(value.decode("ascii","ignore"))
        ret[name] = filter_non_printable(ENTRY_MAP.get(name, lre.text_parse)(value.decode("ascii", "ignore")))
    ret['blocks'] = []
    ret['thumbnails'] = []
    #For the oddball repeating keyword: BlockStatus create an array of them.compatibility:
    for line in text.split('\n'):
        if line.startswith('BlockStatus'):
            ret['blocks'].append(line.strip().replace('BlockStatus:',''))
    #new format
    for k, v in ret.iteritems():
        if k.startswith('block_'):
            ret['blocks'].append(v)
        if k.startswith('thumbnail_'):
            ret['thumbnails'].append(v)

    return ret

def getBlocksFromExpLogJson(explog, excludeThumbnail=False):
    '''Returns array of block dictionary objects defined in explog.txt'''
    # expLog.txt contents from Experiment.log field
    exp_json = json.loads(explog)
    log = json.loads(exp_json['log'])
    return getBlocksFromExpLogDict(log, excludeThumbnail)

def getBlocksFromExpLogDict(explogdict, excludeThumbnail=False):
    '''Returns array of block dictionary objects defined in explog.txt'''
    blocks = []
    # contains regular blocks and a thumbnail block
    blockstatus = explogdict.get('blocks', [])
    if not blockstatus:
        print >> sys.stderr, "ERROR: No blocks found in explog"
    for line in blockstatus:
        # Remove keyword; divide argument by comma delimiter into an array
        args = line.strip().replace('BlockStatus:','').split(',')

        # Remove leading space
        args = [entry.strip() for entry in args]

        # Define Block dictionary object
        #   id_str contains a unique id string
        #   datasubdir contains name of block directory (i.e. 'X0_Y128')
        #   jobid contains job id returned when job is queued
        #   status contains job status string
        block = {'id_str':'',
                'datasubdir':'',
                'jobid':None,
                'autoanalyze':False,
                'analyzeearly':False,
                'status':None}

        if args[0] =='thumbnail' or (args[0] == '0' and args[1] == '0'):
            block['datasubdir'] = 'thumbnail'
            if excludeThumbnail:
                continue
        else:
            block['datasubdir'] = "%s_%s" % (args[0].strip(), args[1].strip())
        block['autoanalyze'] = int(args[4].split(':')[1].strip()) == 1
        block['analyzeearly'] = int(args[5].split(':')[1].strip()) == 1
        block['id_str'] = block['datasubdir']
        print "explog: " + str(block)
        blocks.append(block)

    return blocks

# Moved from crawler_utils.py
def getFlowOrder(rawString):

    '''Parses out a nuke flow order string from entry in explog.txt of the form:
    rawString format:  "4 0 r4 1 r3 2 r2 3 r1" or "4 0 T 1 A 2 C 3 G".'''

    #Initialize return value
    flowOrder = ''

    #Capitalize all lowercase; strip leading and trailing whitespace
    rawString = string.upper(rawString).strip()

    # If there are no space characters, it is 'new' format
    if rawString.find(' ') == -1:
        flowOrder = rawString
    else:
        #Define translation table
        table = {
            "R1": 'G',
            "R2": 'C',
            "R3": 'A',
            "R4": 'T',
            "T": 'T',
            "A": 'A',
            "C": 'C',
            "G": 'G'}
        #Loop thru the tokenized rawString extracting the nukes in order and append to return string
        for c in rawString.split(" "):
            try:
                flowOrder += table[c]
            except KeyError:
                pass

    # Add a safeguard.
    if len(flowOrder) < 4:
        flowOrder = 'TACG'

    return flowOrder


# Moved from crawler.py
def exp_kwargs(d, folder, logobj):
    """Converts the output of `parse_log` to the a dictionary of
    keyword arguments needed to create an ``Experiment`` database object.
    """

    def auto_analyze_block(blockstatus, logobj):
        '''blockstatus is the string from explog.txt starting with keyword BlockStatus.
        Evaluates the AutoAnalyze flag.
        Returns boolean True when argument is 1'''
        try:
            arg = blockstatus.split(',')[4].strip()
            flag = int(arg.split(':')[1]) == 1
        except:
            logobj.error(traceback.format_exc())
            flag = False
        return flag


    identical_fields = ("sample", "cycles", "flows", "project",)
    simple_maps = (
        ("experiment_name", "expName"),
        ("chipbarcode", "chipBarcode"),
        ("user_notes", "notes"),
        ##("seqbarcode", "seqKitBarcode"),
        ("autoanalyze", "autoAnalyze"),
        ("prebeadfind", "usePreBeadfind"),
        ("librarykeysequence", "libraryKey"),
        ("barcodeid", "barcodeKitName"),
        ("isReverseRun", "isReverseRun"),
        ("library", "reference"),
    )

    chiptype = d.get('chiptype','')
    chipversion = d.get('chipversion','')
    if chipversion:
        chiptype = chipversion
    if chiptype.startswith('1.10'):
        chiptype = 'P1.1.17'
    elif chiptype.startswith('1.20'):
        chiptype = 'P1.2.18'
    
    full_maps = (
        ("chipType", chiptype),
        ("pgmName", d.get('devicename', extract_rig(folder))),
        ("log", json.dumps(d, indent=4)),
        ("expDir", folder),
        ("unique", folder),
        ("baselineRun", d.get("runtype") == "STD" or d.get("runtype") == "Standard"),
        ("date", explog_time(d.get("start_time", ""), folder)),
        ("flowsInOrder", getFlowOrder(d.get("image_map", ""))),
        ("reverse_primer", d.get('reverse_primer', 'Ion Kit')),
    )

    derive_attribute_list = ["sequencekitname", "seqKitBarcode", "sequencekitbarcode",
                             "libraryKitName", "libraryKitBarcode"]

    ret = {}
    for f in identical_fields:
        ret[f] = d.get(f, '')
    for k1, k2 in simple_maps:
        ret[k2] = d.get(k1, '')
    for k, v in full_maps:
        ret[k] = v

    for attribute in derive_attribute_list:
        ret[attribute] = ''

    #N.B. this field is not used
    ret['storageHost'] = 'localhost'

    # If Flows keyword is defined in explog.txt...
    if ret['flows'] != "":
        # Cycles should be based on number of flows, not cycles published in log file
        # (Use of Cycles is deprecated in any case! We should be able to enter a random number here)
        ret['cycles'] = int(int(ret['flows']) / len(ret['flowsInOrder']))
    else:
        # ...if Flows is not defined in explog.txt:  (Very-old-dataset support)
        ret['flows'] = len(ret['flowsInOrder']) * int(ret['cycles'])
        logobj.warn("Flows keyword missing: Calculated Flows is %d" % int(ret['flows']))

    if ret['barcodeKitName'].lower() == 'none':
        ret['barcodeKitName'] = ''

    #defensive code to intercept incorrect data coming from explog
    if ret['reference'].lower() == 'none':
        ret['reference'] = ''

    if len(d.get('blocks', [])) > 0:
        ret['rawdatastyle'] = 'tiled'
        ret['autoAnalyze'] = False
        for bs in d['blocks']:
            # Hack alert.  Watch how explogparser.parse_log munges these strings when detecting which one is the thumbnail entry
            # Only thumbnail will have 0,0 as first and second element of the string.
            if '0' in bs.split(',')[0] and '0' in bs.split(',')[1]:
                continue
            if auto_analyze_block(bs, logobj):
                ret['autoAnalyze'] = True
                logobj.debug("Block Run. Detected at least one block to auto-run analysis")
                break
        if ret['autoAnalyze'] is False:
            logobj.debug("Block Run. auto-run whole chip has not been specified")
    else:
        ret['rawdatastyle'] = 'single'

    sequencingKitName = d.get("seqkitname", '')
    #do not replace plan's seqKit info if explog has blank seqkitname
    if sequencingKitName and sequencingKitName != "NOT_SCANNED":
        ret['sequencekitname'] = sequencingKitName

    #in rundb_experiment, there are 2 attributes for sequencingKitBarcode!!
    sequencingKitBarcode = d.get("seqkitpart", '')
    if sequencingKitBarcode and sequencingKitBarcode != "NOT_SCANNED":
        ret['seqKitBarcode'] = sequencingKitBarcode
        ret['sequencekitbarcode'] = sequencingKitBarcode

    libraryKitBarcode = d.get("libbarcode", '')
    if libraryKitBarcode and libraryKitBarcode != "NOT_SCANNED":
        ret['libraryKitBarcode'] = libraryKitBarcode

    libraryKitName = d.get('libkit', '')
    if libraryKitName and libraryKitName != "NOT_SCANNED":
        ret['libraryKitName'] = libraryKitName

    ##note: if PGM is running the old version, there is no isReverseRun in explog.txt.
    isReverseRun = d.get("isreverserun", '')
    if isReverseRun == "Yes":
        ret['isReverseRun'] = True
    else:
        ret['isReverseRun'] = False

    #instrument could have blank runType or be absent all together in explog
    runType = d.get('runtype', "")
    if not runType:
        runType = "GENS"
    ret['runType'] = runType

    platform = d.get('platform', None)
    if platform is None:
        if len(d.get('blocks', [])) > 0:
            platform = 'Proton'
        else:
            platform = 'PGM'
    ret['platform'] = platform.upper()
    
    # Limit input sizes to defined field widths in models.py
    ret['notes'] = ret['notes'][:1024]
    ret['expDir'] = ret['expDir'][:512]
    ret['expName'] = ret['expName'][:128]
    ret['pgmName'] = ret['pgmName'][:64]
    ret['unique'] = ret['unique'][:512]
    ret['project'] = ret['project'][:64]
    ret['sample'] = ret['sample'][:64]
    ret['reference'] = ret['reference'][:64]
    ret['chipBarcode'] = ret['chipBarcode'][:64]
    ret['seqKitBarcode'] = ret['seqKitBarcode'][:64]
    ret['chipType'] = ret['chipType'][:32]
    ret['flowsInOrder'] = ret['flowsInOrder'][:512]
    ret['libraryKey'] = ret['libraryKey'][:64]
    ret['barcodeKitName'] = ret['barcodeKitName'][:128]
    ret['reverse_primer'] = ret['reverse_primer'][:128]
    ret['sequencekitname'] = ret['sequencekitname'][:512]
    ret['sequencekitbarcode'] = ret['sequencekitbarcode'][:512]
    ret['libraryKitName'] = ret['libraryKitName'][:512]
    ret['libraryKitBarcode'] = ret['libraryKitBarcode'][:512]
    ret['runType'] = ret['runType'][:512]

    return ret



def explog_time(timeValue, folder):
    """ Try to construct a timestamp based on the value found in explog.
    Note that Proton and PGM have different timestamp format in their explog.
    If all fails, use the folder-based time
    """

    timestamp = ""
    try:
        timestamp = time.strptime(timeValue, PGM_START_TIME_FORMAT)
    except:
        try:
            timestamp = time.strptime(timeValue, PROTON_START_TIME_FORMAT)
        except:
            return folder_mtime(folder)

    if timestamp:
        return time.strftime(DB_TIME_FORMAT, timestamp)
    else:
        return folder_mtime(folder)


def folder_mtime(folder):
    """Determine the time at which the experiment was performed. In order
    to do this reliably, ``folder_mtime`` tries the following approaches,
    and returns the result of the first successful approach:

    #. Parse the name of the folder, looking for a YYYY_MM_DD type
       timestamp
    #. ``stat()`` the folder and return the ``mtime``.
    """
    import glob

    TIMESTAMP_RE = re.compile(r'R_(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_')
    match = TIMESTAMP_RE.match(os.path.basename(folder))
    if match is not None:
        dt = datetime.datetime(*map(int, match.groups(1)))
        return dt
    else:
        acqfnames = glob.glob(os.path.join(folder, "*.acq"))
        if len(acqfnames) > 0:
            fname = acqfnames[0]
        else:
            fname = folder
        stat = os.stat(fname)
        return datetime.datetime.fromtimestamp(stat.st_mtime)
