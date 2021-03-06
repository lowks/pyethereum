from pyethereum import blocks
from pyethereum import processblock
from pyethereum import rlp
from pyethereum import transactions
from pyethereum import chainmanager
import pyethereum.utils as utils
from remoteblocksdata import data_poc5v23_1
from pyethereum import eth
import logging
import pytest
from tests.utils import set_db
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger()

# customize VM log output to your needs
# hint: use 'py.test' with the '-s' option to dump logs to the console
pblogger = processblock.pblogger
pblogger.log_pre_state = True    # dump storage at account before execution
pblogger.log_post_state = True   # dump storage at account after execution
pblogger.log_block = False       # dump block after TX was applied
pblogger.log_memory = False      # dump memory before each op
pblogger.log_op = True           # log op, gas, stack before each op
pblogger.log_json = False        # generate machine readable output



def load_raw():
    "rlp and hex encoded blocks in multiline file,"
    "each line is in wrong order, which is also expected by chainmanager"
    data = []
    for x in open('tests/raw_remote_blocks_hex.txt'):
        data.extend(reversed(rlp.decode(x.strip().decode('hex'))))
    return rlp.encode(list(reversed(data))).encode('hex')


def do_test(hex_rlp_encoded_data):
    from test_chain import get_chainmanager
    set_db()
    chain_manager = get_chainmanager()
    data = rlp.decode(hex_rlp_encoded_data.decode('hex'))
    transient_blocks = [blocks.TransientBlock(rlp.encode(b)) for b in data]
    assert len(transient_blocks) == 128
    chain_manager.receive_chain(transient_blocks)
    print chain_manager.head


def test_import_remote_chain_blk_128_contract():
    # contract creation
    # error in blk #119
    # do_test(data_poc5v23_1)
    do_test(load_raw())


"""
run like this:
py.test -s -m profiled  tests/test_remoteblocks.py

-s reenables messages to stdout when run by py.test
"""

ACTIVATE_PROFILE_TEST = False
@pytest.mark.skipif(not ACTIVATE_PROFILE_TEST, reason='profiling needs to be activated')
@pytest.mark.profiled
def test_profiled():
    import cProfile
    import StringIO
    import pstats

    def do_cprofile(func):
        def profiled_func(*args, **kwargs):
            profile = cProfile.Profile()
            try:
                profile.enable()
                logger.setLevel(logging.CRITICAL) # don't profile logger
                result = func(*args, **kwargs)
                profile.disable()
                return result
            finally:
                s = StringIO.StringIO()
                ps = pstats.Stats(
                    profile, stream=s).sort_stats('time', 'cum')
                ps.print_stats()
                print s.getvalue()

        return profiled_func

    do_cprofile(test_import_remote_chain_blk_128_contract)()



blk_1228 = "f90897f8d5a065318b69a768fc46233dec15ecd8d4e57c1cfc8bddd066c7d08a038a8864b44aa01dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d4934794e559de5527492bcb42ec68d07df0742a98ec3f1ea0e1caa648f12c7b347c5198abbdf8313faad9d2dd2dba1ab5a04828ad81e88e4ea07f9370b92adf9e995a8beeb456b14f0c47a485de0356c259d4068fb1ec53f14a835a2a7f8207c08609184e72a000830234ee82ea608453beff1d80a00abe68375fb36e243449fc41278842d2e0a47ffb299e825117b5872909bc700ef907bcf901eaf901c3808609184e72a00082138894000000000000000000000000000000000000000064b9015c3631303061323531356235323562363130303063333766323637363337353732353037323639363336353536363130303161353936303030363736333735373235303732363936333635353736383737363836393734363534633639373337343536363130303439353937333061643738303539613330343038303738643933343635353465646535313337613964613938643736383737363836393734363534633639373337343537363837373638363937343635346336393733373435363333306530663631303039383539363030313630323033363034306530663631303038613539363030303335363736333735373235303732363936333635353736373633373537323530373236393633363535363562353235623534363032303532663236313030393435383630303035623532356235343630323035326632363130306132353836303030356235323562353436303230353266321ba07678d2fccc673081d071dee2bee2bf9a4e15c7ac5f47003ad7a3513bf7309f70a0719f527db3fb5304c4658090bcd480e0fd232e08f7c9e0373f4e55deaad201aea070314c27f61ee2ecb655472e5e22a55612bf598ae6635ca812f29a95c34668c0821388f901ecf901c5018609184e72a00082138894000000000000000000000000000000000000000064b9015e36313030613235313562353235623631303030633337663236373633373537323530373236393633363535363631303031613539363030303637363337353732353037323639363336353537363837373638363937343635346336393733373435363631303034393539373330616437383035396133303430383037386439333436353534656465353133376139646139386437363837373078363836393734363534633639373337343537363837373638363937343635346336393733373435363333306530663631303039383539363030313630323033363034306530663631303038613539363030303335363736333735373235303732363936333635353736373633373537323530373236393633363535363562353235623534363032303532663236313030393435383630303035623532356235343630323035326632363130306132353836303030356235323562353436303230353266321ba075ae9b758def52075bc3b3127ae93e6e9a896a961db13682d0e2eff2ee85e893a07c38ad152d6541604e62828603dd2815575c077447301a1768e6db3be69e4745a036369d8edd02260ac6f4884526b211094fde669cf95bcae4acda1f8a4f261379822710f901ecf901c5028609184e72a0008261a894000000000000000000000000000000000000000064b9015e36313030613235313562353235623631303030633337663236373633373537323530373236393633363535363631303031613539363030303637363337353732353037323639363336353537363837373638363937343635346336393733373435363631303034393539373330616437383035396133303430383037386439333436353534656465353133376139646139386437363837373078363836393734363534633639373337343537363837373638363937343635346336393733373435363333306530663631303039383539363030313630323033363034306530663631303038613539363030303335363736333735373235303732363936333635353736373633373537323530373236393633363535363562353235623534363032303532663236313030393435383630303035623532356235343630323035326632363130306132353836303030356235323562353436303230353266321ca0f591d0d0c1fa5ba8a8629769e6a6113f9481c2266f76cea33db8eda01775557fa01f796f5c3932aae676a7382d4cf0252e86820c7dac62817e81b82dbbd821f7b3a02626ab8b289f6b5be3cd9160f14a91076bae776e9a6265b82bab1d04c3a5824b8288b8f901eef901c7038609184e72a0008261a8940000000000000000000000000000000000000000822710b9015e36313030613235313562353235623631303030633337663236373633373537323530373236393633363535363631303031613539363030303637363337353732353037323639363336353537363837373638363937343635346336393733373435363631303034393539373330616437383035396133303430383037386439333436353534656465353133376139646139386437363837373078363836393734363534633639373337343537363837373638363937343635346336393733373435363333306530663631303039383539363030313630323033363034306530663631303038613539363030303335363736333735373235303732363936333635353736373633373537323530373236393633363535363562353235623534363032303532663236313030393435383630303035623532356235343630323035326632363130306132353836303030356235323562353436303230353266321ca037fe36407f35db152c4ba5037f8f5499147ea841b9f01335238d4bc03c51fd10a032f9826564bf1a732236fcd1571faaa1f2c010941da9c8fa420762c9d49e4765a0d948c0d10c3b08a68f481390790bee46c0c957c03050b59fadf83e1a452cbda282ea60c0"

def dump_transactions(hex_rlp_encoded_data):
    "use py.test -s to get logs"
    blk = blocks.TransientBlock(hex_rlp_encoded_data.decode('hex'))
    for tx_lst_serialized, _state_root, _gas_used_encoded in blk.transaction_list:
        tx = transactions.Transaction.create(tx_lst_serialized)
        print tx.to_dict()

@pytest.mark.tx
def test_dump_tx(data=blk_1228):
    return dump_transactions(data)



if __name__ == "__main__":
    """
    this can be run to import raw chain data to a certain db.

    python tests/test_remoteblocks.py rawdatafile testdbdir offset
    e.g.
    python tests/test_remoteblocks.py blocks.0-20k.p23.hexdata testdb 0

    make sure to rm -r the testdb

    data can be created with blockfetcherpatch.py
    """
    import sys

    raw_blocks_fn = sys.argv[1]
    test_db_path = sys.argv[2]
    skip = int(sys.argv[3])
    if len(sys.argv) == 4 or sys.argv[4] != 'silent':
        logging.basicConfig(level=logging.DEBUG)
        global logger
        logger = logging.getLogger()

    print utils
    utils.data_dir.set(test_db_path)

    chain_manager = chainmanager.ChainManager()
    chain_manager.configure(config=eth.create_default_config(), genesis=None)

    fh = open(raw_blocks_fn)
    for i in range(skip):
        fh.readline()

    for hex_rlp_encoded_data in fh:
        hexdata = hex_rlp_encoded_data.strip().decode('hex')
        data = rlp.decode(hexdata)
        # print repr(data)
        blk = blocks.TransientBlock(hexdata)
        print blk.number, blk.hash.encode('hex')
        chain_manager.receive_chain([blk])
        assert blk.hash in chain_manager





